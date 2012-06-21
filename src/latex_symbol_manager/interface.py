from . import  parse_symbols
import sys


def parse_all_symbols(args):
    if not args:
        for x in parse_symbols(sys.stdin, 'stdin'):
            yield x
    else:
        for filename in args:
            with open(filename) as f:
                for x in parse_symbols(f, filename):
                    yield x


def parse_all_sections_symbols(args):
    sections = {}
    symbols = {}

    if not args:
        #logger.debug('Parsing from stdin...')
        for _ in parse_symbols(sys.stdin, 'stdin', sections, symbols):
            pass
    else:
        for filename in args:
            #logger.debug('Parsing %s' % filename)
            with open(filename) as f:
                for _ in parse_symbols(f, filename, sections, symbols):
                    pass
    return sections, symbols

