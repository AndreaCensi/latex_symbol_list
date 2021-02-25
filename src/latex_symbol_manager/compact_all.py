
from optparse import OptionParser
import sys

from  .interface import parse_all_symbols
from  .structures import OtherLine, ParsingError, SymbolSection
from  .symbol import Symbol


def main():
    parser = OptionParser()

    parser.add_option("--select", help="Select by tag")

    parser.add_option("--color", help="Use this color", default=None)

    parser.add_option(
        "--markfirst", help="Mark first command", default=False, action="store_true"
    )

    (options, args) = parser.parse_args()  # @UnusedVariable

    if options.markfirst:
        sys.stdout.write(
            """
           %\\newcommand{\\markfirst}[3]{#3}
        """
        )

    out = sys.stdout

    def comment(el, s):
        s = s.replace("\n", " ")
        out.write("%% %s: %s\n" % (el.symbol, s))

    for el in parse_all_symbols(args):
        if isinstance(el, OtherLine):
            sys.stdout.write(el.line)
            sys.stdout.write("\n")
        elif isinstance(el, Symbol):

            if options.select is not None:
                if not options.select in el.other:
                    comment(el, "Skipped because no field %r" % options.select)
                    continue

            filters = []

            if options.color:
                if el.nargs == 0:

                    def highlight(x):
                        return "{\\color{%s} %s}" % (options.color, x)

                    filters.append(highlight)

            #            if options.deprecated:
            #                if 'deprecated' in el.other and el.nargs == 0:
            #                    def mark_deprecated(x):
            #                        return "{\\color[rgb]{1,0,0} %s}" % x
            #                    filters.append(highlight)

            if options.markfirst:
                if el.nargs == 0:
                    boolname = "used%s" % str(el.symbol[1:])

                    def mark_first(x):
                        return "\\markfirst{%s}{%s}{%s}" % (el.symbol[1:], boolname, x)

                    filters.append(mark_first)

                    sys.stdout.write(
                        "\\newbool{%s}\\setbool{%s}{false}\n" % (boolname, boolname)
                    )

            def wrapper(x):
                for f in filters:
                    x = f(x)
                return x

            sys.stdout.write(el.tex_definition(wrapper=wrapper))
            sys.stdout.write("\n")

        elif isinstance(el, SymbolSection):
            pass
        else:
            raise ParsingError("Unknown element: {0}".format(el), el.where)
            assert False


if __name__ == "__main__":
    main()
