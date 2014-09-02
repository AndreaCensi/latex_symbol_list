import sys
from .parsing_structure import parse_symbols

__all__ = [
    'parse_all_symbols',
    'parse_all_sections_symbols',
]

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

