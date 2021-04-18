from optparse import OptionParser

from latex_symbol_manager.interface import parse_all_sections_symbols
from latex_symbol_manager.script_utils import wrap_script_entry_point
from . import logger
from .find_commands import find_all_commands

__all__ = ["lsm_extract_main"]

usage = """

    %prog -m main.tex -o compact.tex  sources.tex ....

"""


def lsm_extract_main():
    parser = OptionParser(usage)
    parser.add_option("-m", "--main")
    parser.add_option("-o", "--output")
    (options, args) = parser.parse_args()  # @UnusedVariable

    main = options.main
    out = options.output

    sources = args

    f = open(out, "w")

    try:
        sections, symbols = parse_all_sections_symbols(sources)

        logger.info("Loaded %d sections with %d symbols.\n" % (len(sections), len(symbols)))
        if not sections or not symbols:
            raise Exception("Not enough data found.")

        logger.info("Now looking for symbols")
        commands = find_all_commands(main)
        logger.info("I found %d commands" % len(commands))

        done = set()
        todo = set(commands)
        while todo:
            c = todo.pop()
            if c in done:
                continue
            done.add(c)

            if c in symbols:
                logger.info("Found command %r" % c)
                s = symbols[c]
                f.write(s.tex_definition_short() + "\n")
                todo.update(s.symbol_dependencies())
            else:
                logger.warning("Not found %r" % c)

    except:
        raise


def main():
    wrap_script_entry_point(lsm_extract_main, logger)


if __name__ == "__main__":
    main()
