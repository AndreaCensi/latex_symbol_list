import sys
from typing import Dict, List, Tuple

from .parsing_structure import parse_symbols
from .structures import SectionName, SymbolSection
from .symbol import Symbol
from . import logger

__all__ = [
    "parse_all_symbols",
    "parse_all_sections_symbols",
]


def parse_all_symbols(args: List[str]):
    if not args:
        for x in parse_symbols(sys.stdin, "stdin"):
            yield x
    else:
        for filename in args:
            with open(filename) as f:
                for x in parse_symbols(f, filename):
                    yield x


def parse_all_sections_symbols(args: List[str]) -> Tuple[Dict[str, SymbolSection], Dict[str, Symbol]]:
    sections: Dict[SectionName, SymbolSection] = {}
    symbols: Dict[str, Symbol] = {}

    if not args:
        # logger.debug('Parsing from stdin...')
        for _ in parse_symbols(sys.stdin, "stdin", sections, symbols):
            pass
    else:
        for filename in args:
            # logger.debug('Parsing %s' % filename)
            with open(filename) as f:
                for _ in parse_symbols(f, filename, sections, symbols):
                    pass

    for k, v in sections.items():
        # Check subs
        if "/" in v.name:
            parent_name_, _, subname_ = v.name.rpartition("/")
            parent_name = SectionName(parent_name_)
            if not parent_name in sections:
                logger.warning("cannot find parent", name=v.name, parent_name=parent_name)
            else:
                parent = sections[parent_name]
                parent.subs[v.name] = v
                v.parent = parent

    return sections, symbols
