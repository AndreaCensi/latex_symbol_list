import sys
from optparse import OptionParser
from typing import Dict, List

import yaml

from latex_gen import latex_fragment
from latex_symbol_manager.symbol import Symbol
from zuper_ipce import object_from_ipce
from . import logger
from .find_commands import Usage
from .interface import parse_all_sections_symbols
from .script_utils import wrap_script_entry_point
from .structures import NOMENC_EXCLUDE, SEE_ALSO, SORT, SymbolSection


def nomenc_main(args):
    parser = OptionParser()
    parser.add_option("--only", help="YAML file containing the symbols that must be included.")
    parser.add_option("-v", "--verbose", default=False, action="store_true")

    (options, args) = parser.parse_args(args)  # @UnusedVariable

    sections, symbols = parse_all_sections_symbols(args)
    logger.info(f"Loaded {len(sections)} sections with {len(symbols)} symbols.\n")
    if not sections or not symbols:
        raise Exception("Not enough data found.")

    if options.only:
        with open(options.only) as f:
            only_yaml = yaml.load(f, Loader=yaml.Loader)
        only: Dict[str, List[Usage]] = object_from_ipce(only_yaml, Dict[str, List[Usage]])

        v: Symbol
        for k, v in symbols.items():
            if k in only:
                v.usages = only[k]

        have = set(symbols.keys())
        used = set(only)
        have_but_not_used = have.difference(used)
        used_but_not_have = used.difference(have)
        if options.verbose:
            logger.info("have: %s" % have)
            logger.info("used: %s" % used)
            logger.info("have_but_not_used: %s" % have_but_not_used)
            logger.info("used_but_not_have: %s" % used_but_not_have)
        have_and_used = have.intersection(used)
        symbols = dict((k, v) for k, v in list(symbols.items()) if k in have_and_used)
        # TODO: remove symbols from sections

    sections = order_sections(sections)

    create_table_nomenclature(symbols, sections, sys.stdout)


def order_sections(a: Dict[str, object]) -> Dict[str, object]:
    result = {}
    original = list(a)
    while original:
        first = original.pop(0)
        result[first] = a[first]
        children = []
        for x in list(original):
            if x.startswith(first + "/"):
                original.remove(x)
                result[x] = a[x]
            children.append(x)
    return result


def create_table_nomenclature(
    only: Dict[str, Symbol], sections, output, symbols_sort_key=lambda x: x.symbol.lower()
):
    sections = list(sections.values())

    def warn(ss, also_log=True):
        output.write("%% %s\n" % ss)
        if also_log:
            logger.warn(ss)

    s: Symbol
    with latex_fragment(output) as fragment:
        with fragment.longtable(["l", "p{6cm}", "l", "r", "l"]) as table:
            with table.row() as row:
                row.cell_tex("symbol")
                row.cell_tex("meaning")
                row.cell_tex("defined in")
                row.cell_tex("first use")

            for section in sections:
                symbols = [
                    v
                    for _, v in section.symbols.items()
                    if (NOMENC_EXCLUDE not in v.other) and (v.nomenclature or v.nargs == 0)  # and (_ in only)
                ]

                if (not symbols) and (not section.subs):
                    continue

                with table.row() as row:
                    if section.description is None:
                        sct = section.name
                    else:
                        sct = section.description

                    if not sct:
                        sct = "-"

                    if section.parent is None:
                        row.multicolumn_tex(4, "l", f"\\nomencsectionname{{{sct}}}")
                    else:
                        row.multicolumn_tex(4, "c", f"\\nomencsubsectionname{{{sct}}}")

                if section.parent is None:
                    table.hline()

                # symbols.sort(key=symbols_sort_key)

                for s in symbols:
                    # if s.nargs != 0:  # do not write out thes
                    #     continue

                    if s.nomenclature is None:

                        if s.nargs != 0:
                            warn(
                                f"Skipping symbol {s.symbol} because it has args.",
                                False,
                            )
                            continue

                        text = s.desc
                        label = "$%s$" % s.symbol
                    else:
                        text = s.nomenclature.text
                        label = "$%s$" % s.nomenclature.label

                    with table.row() as row:
                        row.cell_tex(label)
                        if s.symbol not in only:
                            text = "\\unused " + text
                        row.cell_tex(text)

                        ref = s.other.get(SEE_ALSO, "")
                        if ref:
                            if not ":" in ref:
                                msg = (
                                    "While considering symbol %s: "
                                    "Could not find a prefix for reference %r "
                                    "so aborting because cref might get confused "
                                    "in a way which is not debuggable" % (s, ref)
                                )
                                raise Exception(msg)
                            row.cell_tex("$\\to$\\cref{%s}" % ref)
                            row.cell_tex("\\pageref{%s}" % ref)
                        else:
                            row.cell_tex("")
                            row.cell_tex("")

                        if s.usages:
                            notnull = [_ for _ in s.usages if _.last_label]
                            if notnull:
                                t = "\\cref{%s}" % notnull[0].last_label

                                row.cell_tex(f"{t}")


def print_nomenclature(symbols, sections: Dict[str, SymbolSection], stream, skip_empty=True):
    def warn(ss, also_log=True):
        stream.write("%% %s\n" % ss)
        if also_log:
            logger.warn(ss)

    groupnames = {}
    for section_name, section in sections.items():
        for symbol_id, symbol in section.symbols.items():
            if symbol_id not in symbols:
                continue
            symbol_name = symbol.symbol[1:]
            if NOMENC_EXCLUDE in symbol.other:
                warn(
                    f"Skipping symbol {symbol.symbol} because of {NOMENC_EXCLUDE}",
                    False,
                )
                continue

            if symbol.nomenclature is None:
                if skip_empty:
                    warn(f"Skipping symbol {symbol.symbol} because of skip_empty.")
                    continue

                if symbol.nargs != 0:
                    warn(f"Skipping symbol {symbol.symbol} because it has args.", False)
                    continue

                text = symbol.desc
                label = "$%s$" % symbol.symbol
            else:
                text = symbol.nomenclature.text
                label = "$%s$" % symbol.nomenclature.label

            text = text.strip()
            # Add period if not there
            if text and text[-1] != ".":
                logger.info("Adding period to %r/%r" % (label, text))
                text += "."

            label = "\\nomencLabel{%s}{%s}" % (symbol_name, label)

            ref = symbol.other.get(SEE_ALSO, "")
            if ref:
                if not ":" in ref:
                    msg = (
                        "While considering symbol %s: "
                        "Could not find a prefix for reference %r "
                        "so aborting because cref might get confused "
                        "in a way which is not debuggable" % (symbol, ref)
                    )
                    raise Exception(msg)
                text += " \\nomencref{%s}" % ref

            ADDPREFIX = f"symbols-{section_name.replace('/', '-')}"
            groupnames[ADDPREFIX] = section.description
            if not SORT in symbol.other:
                sort_options = f"[{ADDPREFIX}]"
            else:
                sort_options = f"[{ADDPREFIX},{symbol.other[SORT]}]"

            if not text:
                warn("No text for %s" % symbol.symbol)
                text = "\\nomencMissExplanation{%s}" % symbol_name

            text = "\\nomencText{%s}{%s}{%s}" % (symbol_name, text, ref)
            s = "\\nomenclature%s{%s}{%s}" % (sort_options, label, text)

            stream.write(s)
            stream.write("\n")

    # \renewcommand{\nomgroup}[1]{%
    #  \ifthenelse{\equal{#1}{V}}{\item[\textbf{Variables}]}{%
    #  \ifthenelse{\equal{#1}{C}}{\item[\textbf{Constants}]}{}}}

    # stream.write('\\renewcommand{\\nomgroup}[1]{%\n')
    # for k, v in groupnames.items():
    #     s = '\\ifthenelse{\\equal{#1}}{K}}{\item[\\textbf{V}]}{%\n'
    #     stream.write(s.replace('K',k).replace('V', v))
    # stream.write('}}}%\n')


def main():
    wrap_script_entry_point(nomenc_main, logger)


if __name__ == "__main__":
    main()
