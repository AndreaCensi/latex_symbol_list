import sys
import traceback
from optparse import OptionParser
from typing import Dict, List, Set

import yaml
from latex_gen import (
    color_rgb,
    emph,
    footnotesize,
    latex_escape,
    latex_fragment,
    texttt,
    verbatim_soft,
)
from latex_gen.tabular import Tabular
from latex_symbol_manager.nomenc import iflabelexists
from zuper_ipce import object_from_ipce

from . import logger
from .find_commands import find_all_commands_in_string, Usage
from .interface import parse_all_sections_symbols
from .structures import NO_INLINE, NO_SUMMARY, SymbolSection
from .symbol import Symbol


def raw_appearance(s):
    return color_rgb(texttt(s), [0.5, 0.5, 0.5])


def write_symbol_rows(
    s, table: Tabular, write_examples: bool, write_desc: bool, example_size: str, is_unused: bool
):
    x = "\\unused " if is_unused else ""

    firstusage = ""
    if s.usages:
        notnull = [_ for _ in s.usages if _.last_label]
        if notnull:
            lastlabel = notnull[0].last_label

            firstusage = iflabelexists(lastlabel, "\\cref{%s}" % lastlabel)

    used_example = False

    if s.nargs == 0:
        with table.row() as row:
            row.cell_tex(raw_appearance(latex_escape(s.symbol)))

            if NO_SUMMARY not in s.other:
                if s.example is None:
                    example = "$%s$" % s.symbol
                else:
                    example = s.example
                row.cell_tex(example)
            else:
                row.cell_tex("(nosummary)")

            if write_desc:
                row.cell_tex(x + s.desc)
            else:
                row.cell_tex(x)

            row.cell_tex(firstusage)

    else:
        # args = ",".join(["..."] * s.nargs)

        if NO_INLINE in s.other:
            example = ""
            example_label = s.symbol
        else:

            if s.example is None:  # and s.nargs > 0:
                put = ["a", "b", "c", "d", "e"]
                args = "".join("{%s}" % _ for _ in put[: s.nargs])
                example = f"${s.symbol}{args}$"
                example_label = f"{s.symbol}{args}"
            else:
                used_example = True
                example = s.example
                example_label = s.example
            # s.example = '$' + example + '$'

        # example = "%s{%s}" % (s.symbol, args)
        with table.row() as row:
            row.cell_tex(raw_appearance(latex_escape(example_label)))
            row.cell_tex(example)
            if write_desc:
                row.cell_tex(x + s.desc)
            else:
                row.cell_tex(x)

    if s.example and write_examples and not used_example:
        with table.row() as row:
            # row.multicolumn_tex(3, "l", head1 + " " + head2)
            row.cell_tex()

            with row.cell() as cell:
                # cell.hspace('2cm') # XXX:

                with cell.fbox() as box:
                    # box.color(0.5, 0.5, 0.5)  # XXX:
                    with box.minipage(example_size) as mp:
                        mp.tex(s.example)
                        # mp.parbreak()
                        # mp.tex(footnotesize(verbatim_soft(s.example)))
            # row.cell()
            row.cell_tex(footnotesize(verbatim_soft(s.example)))


def create_table(
    sections,
    unused_symbols: Set[str],
    output,
    write_examples=True,
    write_desc=True,
    example_size="5.5cm",
    symbols_sort_key=lambda x: x.symbol.lower(),
):
    # logger.info(unused_symbols=unused_symbols)
    with latex_fragment(output) as fragment:

        with fragment.longtable(["l", "p{1cm}", "p{5cm}", "l", "l"]) as table:

            table.row_tex(
                "\\textbf{command}",
                "\\textbf{result}",
                "\\textbf{description}",
                "\\textbf{definition}",
                "\\textbf{first use}",
            )
            table.hline()
            table.hline()
            table.endhead()

            for section in sections:
                table.row_tex("", "", "", "", "")

                with table.row() as row:
                    head1 = raw_appearance(latex_escape(section.name))
                    head2 = emph(section.description)

                    # row.cell_tex(head1)
                    row.multicolumn_tex(5, "l", head1 + " " + head2)

                table.hline()
                if section.parent is None:
                    table.hline()

                symbols = [v for _, v in list(section.symbols.items())]
                symbols.sort(key=symbols_sort_key)
                for s in symbols:
                    is_unused = s.symbol in unused_symbols
                    if is_unused:
                        print(f"% symbol {s.symbol} not used")
                    write_symbol_rows(
                        s,
                        table,
                        write_examples=write_examples,
                        write_desc=write_desc,
                        example_size=example_size,
                        is_unused=is_unused,
                    )


def create_table_minimal(
    sections,
    unused_symbols: Set[str],
    output,
    symbols_sort_key=lambda x: x.symbol.lower(),
):
    with latex_fragment(output) as fragment:
        with fragment.longtable(["c", "l"]) as table:

            for section in sections:
                with table.row() as row:
                    row.multicolumn_tex(2, "l", section.description)

                table.hline()
                if section.parent is None:
                    table.hline()

                symbols = [v for _, v in list(section.symbols.items())]
                symbols.sort(key=symbols_sort_key)
                for s in symbols:
                    if s.nargs != 0:  # do not write out thes
                        continue

                    with table.row() as row:
                        row.cell_tex("$%s$" % s.symbol)
                        row.cell_tex(s.desc)


def get_symbols_used_in_definitions(symbols: Dict[str, Symbol]) -> Set[str]:
    res = set()
    for s in symbols.values():
        defi = s.tex

        res.update(set(find_all_commands_in_string(defi)))
    return res


def main():
    parser = OptionParser()
    parser.add_option("--only", help="YAML file containing the symbols that must be included.")
    parser.add_option(
        "--sort_sections_alpha",
        help="Sort sections alphabetically",
        default=False,
        action="store_true",
    )

    parser.add_option(
        "--verbose",
        default=False,
        action="store_true",
    )
    parser.add_option(
        "--sort_symbols_alpha",
        help="Sort symbols alphabetically",
        default=False,
        action="store_true",
    )

    parser.add_option("--style", help="Type of table (full*, minimal, small, medium)", default="full")

    # TODO: flat option

    (options, args) = parser.parse_args()  # @UnusedVariable

    try:
        sections, symbols = parse_all_sections_symbols(args)

        if options.only:
            with open(options.only) as f:
                only_yaml = yaml.load(f, Loader=yaml.Loader)
            only = object_from_ipce(only_yaml, Dict[str, List[Usage]])

            more = get_symbols_used_in_definitions(symbols)
            if options.verbose:
                logger.info(f"found more in definitions", more=more)
            have = set(symbols.keys())

            v: Symbol
            for k, v in symbols.items():
                if k in only:
                    v.usages = only[k]

            used = set(only)
            used.update(more)
            have_but_not_used = have.difference(used)
            used_but_not_have = used.difference(have)
            if options.verbose:
                logger.debug(have=have)
                logger.debug(used=used)
                logger.debug(have_but_not_used=have_but_not_used)
                logger.debug(used_but_not_have=used_but_not_have)
            # have_and_used = have.intersection(used)
            # used_symbols = set(dict((k, v) for k, v in list(symbols.items()) if k in have_and_used))
            # TODO: remove symbols from sections
        else:
            have_but_not_used = set()

        from .nomenc import order_sections

        # logger.info('before ordering', sections=list(sections))
        sections = order_sections(sections)
        # logger.info('after ordering', sections=list(sections))

        show_hierarchy(sections)
        logger.info("Loaded %d sections with %d symbols.\n" % (len(sections), len(symbols)))
        if not sections or not symbols:
            raise Exception("Not enough data found.")

        # which = args
        which = None  # XXX add switch
        if which:
            selected = dict([(k, v) for (k, v) in list(sections.items()) if k in which])
        else:
            selected = sections

        if not selected:
            raise Exception("No sections selected (which: %r)" % which)

        ordered = [v for k, v in list(selected.items())]
        # if options.sort_sections_alpha:
        #     key = lambda v: v.name
        # else:
        #     key = lambda v: v.definition_order
        # ordered.sort(key=key)

        if options.sort_symbols_alpha:
            key = lambda v: v.symbol.lower
        else:
            key = lambda v: v.definition_order

        def full():
            create_table(
                ordered,
                have_but_not_used,
                sys.stdout,
                write_examples=True,
                write_desc=True,
                symbols_sort_key=key,
            )

        def medium():
            create_table(
                ordered,
                have_but_not_used,
                sys.stdout,
                write_examples=False,
                write_desc=True,
                symbols_sort_key=key,
            )

        def small():
            create_table(
                ordered,
                have_but_not_used,
                sys.stdout,
                write_examples=False,
                write_desc=False,
                symbols_sort_key=key,
            )

        def minimal():
            create_table_minimal(ordered, have_but_not_used, sys.stdout, symbols_sort_key=key)

        styles = {"minimal": minimal, "full": full, "small": small, "medium": medium}
        if options.style not in styles:
            msg = "No known style %r. Valid options: %s." % (
                options.style,
                list(styles.keys()),
            )
            raise Exception(msg)
        styles[options.style]()

    except Exception as e:
        sys.stderr.write(traceback.format_exc())
        sys.stderr.write("\n")
        sys.exit(-1)


def show_hierarchy(s: Dict[str, SymbolSection]):
    ss = {}
    for k, v in s.items():
        ss[k] = list(v.subs)
    logger.info("hierarchy", ss=ss)


if __name__ == "__main__":
    main()
