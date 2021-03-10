import glob
import os
from dataclasses import dataclass
from optparse import OptionParser
from typing import Iterator, List, Optional, Tuple, Union

from zuper_commons.fs import read_ustring_from_utf8_file, write_ustring_to_utf8_file
from zuper_commons.types import ZValueError
from . import logger

usage = """ 
 
"""


@dataclass
class Equation:
    start: int
    label: Optional[str]
    a: str
    content: str
    b: str
    translation: Optional[str]


def find_chunks(a: str, b: str, data: str) -> Iterator[Tuple[int, str]]:
    nbef = 0
    while data:
        if a not in data:
            break
        i = data.index(a)
        ne = data[i + len(a) :]
        try:
            j = ne.index(b)
        except ValueError:
            logger.error("Cannot find closure", ne=ne, b=b)
            break
        chunk = data[i + len(a) : i + len(a) + j]

        yield nbef, chunk
        data = data[i + len(a) + len(chunk) + len(b) :]
        nbef += i + len(a) + len(chunk) + len(b)


def find_label(data: str) -> Optional[str]:
    start = "\\label{"
    if start in data:
        i = data.index(start)
        data0 = data[i + len(start) :]
        j = data0.index("}")
        return data0[:j]
    else:
        return None


def find_in_file(a, b, data) -> Iterator[Equation]:
    for nbef, chunk in find_chunks(a, b, data):
        label = find_label(chunk)
        if label:
            r = "\\label{" + label + "}"
            chunk = chunk.replace(r, "{}")

        chunk = chunk.rstrip()
        chunk = remove_all_labels(chunk)
        yield Equation(nbef, label, a, chunk, b, None)


def remove_all_labels(chunk: str) -> str:
    while True:
        label = find_label(chunk)
        if not label:
            return chunk
        r = "\\label{" + label + "}"
        chunk = chunk.replace(r, "{}")


@dataclass
class Found:
    prefix: str
    inside: str
    postfix: str


def get_subs(chunk: str, possibilities: List[Tuple[str, str]]) -> Iterator[Union[str, Found]]:
    for start, stop in possibilities:
        if start in chunk:
            i = chunk.index(start)
            yield chunk[:i]
            data0 = chunk[i + len(start) :]
            j = data0.index(stop)
            inside = data0[:j]
            chunk = data0[j + len(stop) :]
            yield Found(start, inside, stop)
            yield from get_subs(chunk, possibilities)
            break


def get_label_prefix(x: str) -> str:
    a, _, c = x.rpartition(":")
    return a


def is_equation_label(x: str) -> bool:
    return get_label_prefix(x) in ["eq"]


def is_definition_label(x: str) -> bool:
    return get_label_prefix(x) in ["def"]


def is_table_label(x: str) -> bool:
    return get_label_prefix(x) in ["tab"]


def find_equation_in_file(data: str) -> Iterator[Equation]:
    options = [
        ("\\begin{equation}", "\\end{equation}", "equation*"),
        ("\\begin{equation*}", "\\end{equation*}", "equation*"),
        ("\\begin{align}", "\\end{align}", "align"),
        ("\\begin{align*}", "\\end{align*}", "align*"),
    ]
    for a, b, newenv in options:
        for eq in find_in_file(a, b, data):
            if eq.label and not is_equation_label(eq.label):
                logger.error("Found weird label for equation", label=eq.label, eq=eq)
                continue
            chunk = eq.content
            for x in [".", ","]:
                if chunk.endswith(x):
                    chunk = chunk[:-1]
            eq.content = chunk
            translation = "\\begin{" + newenv + "}" + eq.content + "\\end{" + newenv + "}\n"
            eq.translation = translation
            yield eq


def find_definition_in_file(data: str) -> Iterator[Equation]:
    options = [
        ("\\begin{definition}", "\\end{definition}", "definition*"),
        ("\\begin{ctdefinition}", "\\end{ctdefinition}", "definition*"),
    ]
    for a, b, newenv in options:

        for eq in find_in_file(a, b, data):
            if eq.label and not is_definition_label(eq.label):
                logger.error("Found weird label", label=eq.label, eq=eq)
                continue

            translation = (
                "\\pagecolor{white}\n\\begin{" + newenv + "}" + eq.content + "\\end{" + newenv + "}\n"
            )
            translation = translation.replace("{equation}", "{equation*}")
            translation = translation.replace("{align}", "{align*}")

            eq.translation = translation
            yield eq


def find_others(data: str) -> Iterator[Equation]:
    options = [
        ("\\begin{lemma}", "\\end{lemma}", "lemma*", ["lem"]),
        ("\\begin{lemma*}", "\\end{lemma*}", "lemma*", ["lem"]),
    ]
    for a, b, newenv, labelprefixes in options:

        for eq in find_in_file(a, b, data):
            if eq.label and not get_label_prefix(eq.label) in labelprefixes:
                logger.error("Found weird label", label=eq.label, eq=eq)
                continue

            translation = (
                "\\pagecolor{white}\n\\begin{" + newenv + "}" + eq.content + "\\end{" + newenv + "}\n"
            )
            translation = translation.replace("{equation}", "{equation*}")
            translation = translation.replace("{align}", "{align*}")

            eq.translation = translation
            yield eq


def find_tables_in_file(data: str) -> Iterator[Equation]:
    options = [
        ("\\begin{table}", "\\end{table}", "table"),
        ("\\begin{table*}", "\\end{table*}", "table"),
        ("\\begin{margintable}", "\\end{margintable}", "table"),
    ]
    for a, b, newenv in options:

        for eq in find_in_file(a, b, data):
            if eq.label and not is_table_label(eq.label):
                logger.error("Found weird label", label=eq.label, eq=eq)
                continue

            translation = (
                "\\renewcommand{\\caption}[1]{}\n"
                +
                # "\\pagecolor{white}\n\\begin{" + newenv + "}" + eq.content + "\\end{" + newenv + "}\n"
                eq.content
            )
            # translation = translation.replace("{equation}", "{equation*}")
            # translation = translation.replace("{align}", "{align*}")

            eq.translation = translation
            yield eq


def remove_tex_comments(data: str) -> str:
    lines = data.split("\n")
    b = []
    for line in lines:
        if "%" in line:
            i = line.index("%")
            line = line[:i]
            if line.strip():
                b.append(line)
        else:
            b.append(line)
    return "\n".join(b)


def main():
    parser = OptionParser(usage)
    parser.add_option("--output", help="Output directory")
    parser.add_option("--search", help="Search directory")
    (options, args) = parser.parse_args()  # @UnusedVariable
    if args:
        raise Exception()
    out = options.output

    search = options.search
    filenames = glob.glob(search + "/**/*.tex", recursive=True)

    for filename in filenames:
        rel_filename = os.path.relpath(filename, search)
        # logger.info(filename=filename, rel_filename=rel_filename)
        data = read_ustring_from_utf8_file(filename)
        data = remove_tex_comments(data)
        equations = list(find_equation_in_file(data))
        others = list(find_others(data))
        # equations = sorted(equations, key=(lambda x: x.start))
        definitions = list(find_definition_in_file(data))
        tables = list(find_tables_in_file(data))
        stuff = equations + definitions + tables + others
        if stuff and False:
            logger.info(f=filename, n=len(equations), df=len(definitions))

        known_labels = {}
        for i, eq in enumerate(stuff):
            currfile, _ = os.path.splitext(os.path.basename(filename))
            if not eq.label:
                continue
            if eq.label in known_labels:
                msg = "Found two identical labels"
                raise ZValueError(msg, label=eq.label, filename=filename, eq1=known_labels[eq.label], eq2=eq)
            known_labels[eq.label] = eq
            label = eq.label.replace(":", "_")
            base, _ = os.path.splitext(rel_filename)
            fn = os.path.join(out, base, label + ".texi")
            write_ustring_to_utf8_file(eq.translation, fn, quiet=True)


if __name__ == "__main__":
    main()
