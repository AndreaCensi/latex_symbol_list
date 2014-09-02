from latex_gen import (color_rgb, small, verbatim_soft, latex_escape, texttt,
    emph, latex_fragment)
from optparse import OptionParser
import sys
from .interface import parse_all_sections_symbols


def raw_appearance(s):
    return color_rgb(texttt(s), [0.5, 0.5, 0.5])


def write_symbol_rows(s, table, write_examples, example_size):
    if s.nargs == 0:
        with table.row() as row:
            row.cell_tex(raw_appearance(latex_escape(s.symbol)))
            if not 'nosummary' in s.other:
                row.cell_tex('$%s$' % s.symbol)
            else:
                row.cell_tex('(nosummary)')
            row.cell_tex(s.desc)
    else:
        args = ",".join(['...'] * s.nargs)
        example = '%s{%s}' % (s.symbol, args)
        with table.row() as row:
            row.cell_tex(raw_appearance(latex_escape(example)))
            row.cell_tex('')
            row.cell_tex(s.desc)

    if s.example and write_examples:

        with table.row() as row:
            row.cell_tex()
            row.cell_tex()
            with row.cell() as cell:
                # cell.hspace('2cm') # XXX:

                with cell.fbox() as box:
                    box.color(0.5, 0.5, 0.5)  # XXX:
                    with box.minipage(example_size) as mp:
                        mp.tex(s.example)
                        mp.parbreak()
                        mp.tex(small(verbatim_soft(s.example)))


def create_table(sections, output, write_examples=True, example_size='8cm',
                 symbols_sort_key=lambda x: x.symbol.lower()):

    with latex_fragment(output) as fragment:
        with fragment.longtable(['l', 'l', 'l']) as table:

            # table.row_tex('Symbol', '\\TeX command', 'description')
            # table.hline()
            # table.hline() 

            for section in sections:
                table.row_tex('', '', '')

                with table.row() as row:
                    row.cell_tex(raw_appearance(latex_escape(section.name)))
                    row.multicolumn_tex(2, 'l', emph(section.description))

                table.hline()
                if section.parent is None:
                    table.hline()

                symbols = [v for _, v in section.symbols.items()]
                symbols.sort(key=symbols_sort_key)
                for s in symbols:
                    write_symbol_rows(s, table,
                                      write_examples=write_examples,
                                      example_size=example_size)


def create_table_minimal(sections, output,
                         symbols_sort_key=lambda x: x.symbol.lower()):
    with latex_fragment(output) as fragment:
        with fragment.longtable(['c', 'l']) as table:

            for section in sections:
                with table.row() as row:
                    row.multicolumn_tex(2, 'l', section.description)

                table.hline()
                if section.parent is None:
                    table.hline()

                symbols = [v for _, v in section.symbols.items()]
                symbols.sort(key=symbols_sort_key)
                for s in symbols:
                    if s.nargs != 0:  # do not write out thes
                        continue

                    with table.row() as row:
                        row.cell_tex('$%s$' % s.symbol)
                        row.cell_tex(s.desc)


def main():
    parser = OptionParser()

    parser.add_option("--sort_sections_alpha",
                      help="Sort sections alphabetically",
                      default=False, action='store_true')

    parser.add_option("--sort_symbols_alpha",
                      help="Sort symbols alphabetically",
                      default=False, action='store_true')

    parser.add_option("--style", help="Type of table", default='full')

    # TODO: flat option

    (options, args) = parser.parse_args() #@UnusedVariable

    try:
        sections, symbols = parse_all_sections_symbols(args)

        sys.stderr.write('Loaded %d sections with %d symbols.\n' %
                         (len(sections), len(symbols)))
        if not sections or not symbols:
            raise Exception('Not enough data found.')

        # which = args
        which = None #XXX add switch
        if which:
            selected = dict([(k, v)
                             for (k, v) in sections.items() if k in which])
        else:
            selected = sections

        if not selected:
            raise Exception('No sections selected (which: %r)' % which)

        ordered = [v for k, v in selected.items()]
        if options.sort_sections_alpha:
            key = lambda v: v.name
        else:
            key = lambda v: v.definition_order
        ordered.sort(key=key)

        if options.sort_symbols_alpha:
            key = lambda v: v.symbol.lower
        else:
            key = lambda v: v.definition_order

        def full():
            create_table(ordered, sys.stdout,
                         write_examples=True, symbols_sort_key=key)

        def minimal():
            create_table_minimal(ordered, sys.stdout, symbols_sort_key=key)

        styles = {'minimal': minimal, 'full': full}
        if options.style not in styles:
            msg = ('No known style %r. Valid options: %s.' %
                   (options.style, styles.keys()))
            raise Exception(msg)
        styles[options.style]()

    except Exception as e:
        sys.stderr.write(str(e))
        sys.stderr.write('\n')
        sys.exit(-1)

if __name__ == '__main__':
    main()

