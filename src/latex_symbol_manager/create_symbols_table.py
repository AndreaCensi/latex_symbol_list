import sys
import traceback
from optparse import OptionParser
from typing import Dict, Set

import yaml
from latex_gen import (color_rgb, emph, footnotesize, latex_escape, latex_fragment, texttt, verbatim_soft)

from latex_symbol_manager.programs.collect import find_all_commands_in_string
from . import logger, NO_INLINE, NO_SUMMARY, Symbol
from .interface import parse_all_sections_symbols


def raw_appearance(s):
    return color_rgb(texttt(s), [0.5, 0.5, 0.5])


def write_symbol_rows(s, table, write_examples: bool, write_desc: bool, example_size, is_unused: bool):
    x = '\\unused ' if is_unused else ''

    used_example = False

    if s.nargs == 0:
        with table.row() as row:
            row.cell_tex(raw_appearance(latex_escape(s.symbol)))

            if not NO_SUMMARY in s.other:
                row.cell_tex("$%s$" % s.symbol)
            else:
                row.cell_tex("(nosummary)")
            if write_desc:
                row.cell_tex(x + s.desc)
            else:
                row.cell_tex()
    else:
        # args = ",".join(["..."] * s.nargs)

        if NO_INLINE in s.other:
            example = ''
            example_label = s.symbol
        else:

            if s.example is None:  # and s.nargs > 0:
                put = ['a', 'b', 'c', 'd', 'e']
                args = "".join('{%s}' % _ for _ in put[:s.nargs])
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
                row.cell_tex()

    if s.example and write_examples and not (used_example):
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
    example_size="5cm",
    symbols_sort_key=lambda x: x.symbol.lower(),
):
    with latex_fragment(output) as fragment:

        with fragment.longtable(["l", "l", "l"]) as table:

            # table.row_tex('Symbol', '\\TeX command', 'description')
            # table.hline()
            # table.hline()

            for section in sections:
                table.row_tex("", "", "")

                with table.row() as row:
                    head1 = raw_appearance(latex_escape(section.name))
                    head2 = emph(section.description)

                    # row.cell_tex(head1)
                    row.multicolumn_tex(3, "l", head1 + " " + head2)

                table.hline()
                if section.parent is None:
                    table.hline()

                symbols = [v for _, v in list(section.symbols.items())]
                symbols.sort(key=symbols_sort_key)
                for s in symbols:
                    is_unused = s.symbol in unused_symbols
                    if is_unused:
                        print(f'% symbol {s.symbol} not used')
                    write_symbol_rows(
                        s,
                        table,
                        write_examples=write_examples,
                        write_desc=write_desc,
                        example_size=example_size,
                        is_unused=is_unused,
                    )


def create_table_minimal(sections, unused_symbols: Set[str], output,
                         symbols_sort_key=lambda x: x.symbol.lower()):
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
    parser.add_option(
        "--only", help="YAML file containing the symbols" "that must be included."
    )
    parser.add_option(
        "--sort_sections_alpha",
        help="Sort sections alphabetically",
        default=False,
        action="store_true",
    )

    parser.add_option(
        "--sort_symbols_alpha",
        help="Sort symbols alphabetically",
        default=False,
        action="store_true",
    )

    parser.add_option("--style", help="Type of table", default="full")

    # TODO: flat option

    (options, args) = parser.parse_args()  # @UnusedVariable

    try:
        sections, symbols = parse_all_sections_symbols(args)

        if options.only:
            with open(options.only) as f:
                only = yaml.load(f)

            more = get_symbols_used_in_definitions(symbols)
            logger.info(f'found more in definitions', more=more)
            have = set(symbols.keys())

            used = set(only)
            used.update(more)
            have_but_not_used = have.difference(used)
            used_but_not_have = used.difference(have)
            # if options.verbose:
            logger.info(have=have)
            logger.info(used=used)
            logger.info(have_but_not_used=have_but_not_used)
            logger.info(used_but_not_have=used_but_not_have)
            # have_and_used = have.intersection(used)
            # used_symbols = set(dict((k, v) for k, v in list(symbols.items()) if k in have_and_used))
            # TODO: remove symbols from sections
        else:
            have_but_not_used = set()

        from .programs.nomenc import order_sections
        sections = order_sections(sections)
        logger.info(sorted=list(sections))
        logger.info(
            "Loaded %d sections with %d symbols.\n" % (len(sections), len(symbols))
        )
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
            create_table(ordered, have_but_not_used, sys.stdout, write_examples=True, write_desc=True,symbols_sort_key=key)

        def medium():
            create_table(ordered, have_but_not_used, sys.stdout, write_examples=False, write_desc=True,symbols_sort_key=key)

        def small():
            create_table(ordered, have_but_not_used, sys.stdout, write_examples=False, write_desc=False, symbols_sort_key=key)


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


if __name__ == "__main__":
    main()
