from .. import parse_all_sections_symbols, logger
from optparse import OptionParser
import sys


def main():
    parser = OptionParser()

    parser.add_option("--include",
                      help="Sections to include (comma separated)",
                      default="all")

    parser.add_option("--blue", default="", help="Color these in blue")
    parser.add_option("--red", default="", help="Color these in red")
    parser.add_option("--green", default="", help="Color these in green")

    (options, args) = parser.parse_args() #@UnusedVariable

    sections, symbols = parse_all_sections_symbols(args)

    logger.info('Loaded %d sections with %d symbols.\n'
                     % (len(sections), len(symbols)))

    if not sections or not symbols:
        raise Exception('Not enough data found.')

    def get_sections(which):
        if not which:
            return []
        names = which.split(',')

        l = []
        for x in names:
            lx = []
            for k in sections.keys():
                if x in k:
                    lx.append(sections[k])

            if x == 'all':
                lx.extend(sections.values())
            if not lx:
                raise Exception('Section %s not found in %s'
                                % (x, sections.keys()))

            l.extend(lx)
        return l

    # which = args
    selected = get_sections(options.include)
    color_blue = get_sections(options.blue)
    color_red = get_sections(options.red)
    color_green = get_sections(options.green)

    logger.info('Selected: %s' % selected)

    wrap_red = lambda x: "{\\color[rgb]{0.5,0,0} %s}" % x
    wrap_blue = lambda x: "{\\color[rgb]{0,0,0.5} %s}" % x
    wrap_green = lambda x: "{\\color[rgb]{0,0.3,0} %s}" % x

    f = sys.stdout

    if not selected:
        raise Exception('No sections selected (which: %r)' % options.sections)

    for section in selected:
        wrapper = None
        if section in color_green:
            wrapper = wrap_green
        if section in color_blue:
            wrapper = wrap_blue
        if section in color_red:
            wrapper = wrap_red

        for symbol in section.symbols.values():
            f.write(symbol.tex_definition(wrapper=wrapper))
            f.write('\n')


if __name__ == '__main__':
    main()
