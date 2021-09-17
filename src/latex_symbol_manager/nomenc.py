import sys
from optparse import OptionParser
from typing import Dict, List, Literal

import yaml
from latex_gen import latex_fragment
from zuper_ipce import object_from_ipce

from . import logger
from .find_commands import Usage
from .interface import parse_all_sections_symbols
from .script_utils import wrap_script_entry_point
from .structures import NOMENC_EXCLUDE, SEE_ALSO, SymbolSection
from .symbol import Symbol


def nomenc_main(args):
    parser = OptionParser()
    parser.add_option("--only", help="YAML file containing the symbols that must be included.")

    parser.add_option("--style", default="small", help="One of  (small, medium, large)")
    parser.add_option(
        "--allow-empty", default=False, action="store_true", help="Also allow empty symbols descriptions"
    )
    parser.add_option("-v", "--verbose", default=False, action="store_true")

    (options, args) = parser.parse_args(args)  # @UnusedVariable

    style = options.style
    assert style in ("small", "medium", "large"), style
    sections: Dict[str, SymbolSection]
    symbols: Dict[str, Symbol]
    sections, symbols = parse_all_sections_symbols(args)
    logger.info(f"Loaded {len(sections)} sections with {len(symbols)} symbols.\n")
    if not sections or not symbols:
        raise Exception("Not enough data found.")

    allow_empty = options.allow_empty
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
            logger.info(
                have=have, used=used, have_but_not_used=have_but_not_used, used_but_not_have=used_but_not_have
            )
        have_and_used = have.intersection(used)
        symbols = dict((k, v) for k, v in list(symbols.items()) if k in have_and_used)
        # TODO: remove symbols from sections

    # logger.info('before ordering', sections=list(sections))
    sections = order_sections(sections)

    # logger.info('after ordering', sections=list(sections))

    def is_section_empty(s: SymbolSection):
        return (NOMENC_EXCLUDE in s.attrs) or ((not s.subs) and (not s.symbols))

    def is_symbol_to_remove(symbol: Symbol):
        if style == "small":
            return (NOMENC_EXCLUDE in symbol.other) or ((not symbol.desc) and (not symbol.example))
        elif style in ["medium", "large"]:
            # also care about SEE_ALSO
            return (NOMENC_EXCLUDE in symbol.other) or (
                (not symbol.desc) and (not symbol.example) and (SEE_ALSO not in symbol.other)
            )
        else:
            assert False, style

    if not allow_empty:
        for section_name, section in sections.items():
            excluded = []
            for symbol_name, symbol in list(section.symbols.items()):
                if is_symbol_to_remove(symbol):
                    excluded.append(symbol_name)
                    section.symbols.pop(symbol_name)
            if excluded:
                logger.info(
                    f"Excluding from section {section_name!r} these symbols because there is no descrition.",
                    excluded=excluded,
                )

        for i in range(10):
            for section_name, section in list(sections.items()):
                for sub_section_name, sub_section in list(section.subs.items()):
                    if is_section_empty(sub_section):
                        logger.info(
                            f"Excluding from section {section_name!r} the subsection {sub_section_name!r} "
                            f"because there is no symbol and no sub."
                        )
                        section.subs.pop(sub_section_name)
            for section_name, section in list(sections.items()):
                if is_section_empty(section):
                    logger.info(
                        f"Excluding  section {section_name!r}  because " f"there is no symbol and no sub."
                    )

                    sections.pop(section_name)

    create_table_nomenclature(symbols, sections, style, sys.stdout)


def order_sections(a: Dict[str, SymbolSection]) -> Dict[str, SymbolSection]:
    tops = {}
    for k, v in a.items():
        if v.parent is None:
            tops[k] = v

    result = {}

    def copy_now(sn: str, s: SymbolSection):
        result[sn] = s
        orde = sorted(s.subs)
        for k in orde:
            copy_now(k, s.subs[k])

    for k, v in tops.items():
        copy_now(k, v)
    return result


def create_table_nomenclature(
    only: Dict[str, Symbol],
    sections: Dict[str, SymbolSection],
    style: Literal["small", "medium", "large"],
    output,  # symbols_sort_key=lambda x: x.symbol.lower()
):
    sections = list(sections.values())

    def warn(ss, also_log=True):
        output.write("%% %s\n" % ss)
        if also_log:
            logger.warn(ss)

    s: Symbol
    with latex_fragment(output) as fragment:
        if style == "large":
            size_second = "p{6cm}"
        elif style == "medium":
            size_second = "p{8cm}"
        else:
            size_second = "p{10cm}"

        with fragment.longtable(["p{2cm}", size_second, "l", "l"]) as table:
            with table.row() as row:
                row.cell_tex("\\textbf{symbol}")
                row.cell_tex("\\textbf{meaning}")

                if style == "small":
                    pass
                elif style == "medium":
                    row.cell_tex("\\textbf{defined in}")
                elif style == "large":
                    row.cell_tex("\\textbf{defined in}")
                    row.cell_tex("\\textbf{first use}")
                else:
                    assert False

            table.hline()
            table.hline()
            table.endhead()

            for section in sections:
                symbols = [
                    v
                    for _, v in section.symbols.items()
                    if (NOMENC_EXCLUDE not in v.other) and (v.nomenclature or v.nargs == 0)  # and (_ in only)
                ]
                #
                # if (not symbols) and (not section.subs):
                #     continue

                with table.row() as row:
                    if section.description is None:
                        sct = section.name
                    else:
                        sct = section.description

                    if not sct:
                        sct = "-"

                    levels = section.name.count("/")

                    if section.parent is None:
                        row.multicolumn_tex(4, "l", f"\\nomencsectionname{{{sct}}}")
                    else:
                        row.multicolumn_tex(4, "c", "\quad" * levels + f"\\nomencsubsectionname{{{sct}}}")

                if section.parent is None:
                    table.hline()

                # symbols.sort(key=symbols_sort_key)

                for s in symbols:
                    is_unused = s.symbol not in only
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
                        # if is_unused:
                        #     text = "\\unused " + text
                        row.cell_tex(text)

                        if style in ["medium", "large"]:
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
                                tex = "$\\to$\\cref{%s} on p.\\pageref{%s}" % (ref, ref)
                                tex = "\\iflabelexists{%s}{%s}" % (ref, tex)
                                row.cell_tex(tex)
                                # row.cell_tex("on " % ref)
                            else:
                                row.cell_tex("")
                                # row.cell_tex("")
                        if style in ["large"]:
                            if s.usages:
                                notnull = [_ for _ in s.usages if _.last_label]
                                if notnull:
                                    l = notnull[0].last_label
                                    if ref != l:
                                        t2 = "p.\\pageref{%s} near~\\cref{%s}" % (l, l)
                                        t2 = "\\iflabelexists{%s}{%s}" % (l, t2)
                                    else:
                                        t2 = ""
                                else:
                                    t2 = ""
                            else:
                                t2 = ""

                            if is_unused:
                                t2 += "\\unused"
                            row.cell_tex(t2)


def main():
    wrap_script_entry_point(nomenc_main, logger)


if __name__ == "__main__":
    main()
