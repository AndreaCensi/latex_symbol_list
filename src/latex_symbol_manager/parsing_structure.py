from collections import namedtuple
from .parsing import parse_stream
import sys
from .lookahead import Lookahead
from .structures import NewCommand, OtherLine, \
    SpecialComment, SymbolSection, ParsingError

from .symbol import Symbol

def parse_symbols(stream, filename, sections=None, symbols=None):
    current_section = None
    if sections is None: sections = {}
    if symbols is None: symbols = {}
    
    peek = Lookahead(parse_stream(stream, filename))

    for el in peek:
        if isinstance(el, NewCommand):
            if current_section is None:
                raise ParsingError('No section defined yet', el.where)
            
            next = peek.lookahead(0)
            if isinstance(next, SpecialComment) and next.tag == 'example':
                example = "\n".join(peek.next().lines)
            else:
                example = None 
    
            tag = current_section.name
    
            if el.command in symbols:
                raise ParsingError('Already know symbol %s from %r.' % 
                                   (el.command, symbols[el.command].where), el.where)
            definition_order = len(symbols)
            s = Symbol(el.command, definition_order=definition_order, 
                        tex=el.body, desc=el.comment, tag=tag,
                       long=None, example=example, nargs=el.nargs, where=el.where)
            symbols[el.command] = s 
            current_section.symbols[el.command] = s
            
            yield s
            
        elif isinstance(el, SpecialComment):
            if el.tag == 'section':
                if not ':' in el.lines[0] or len(el.lines) > 1:
                    raise ParsingError('Malformed section tag: {0!r}'.format(el), el.where)
                name, description = el.lines[0].split(':')
                # Check subs
                if '/' in name:
                    parent = name.split('/')[0].strip()
                    if not parent in sections:
                        raise ParsingError('Could not find parent section %r' % parent,
                                           el.where)
                else:
                    parent = None
                
                definition_order = len(sections)
                
                section = SymbolSection(name.strip(), description.strip(),
                                        {}, parent, {}, el.where, definition_order)
                if section.name in sections:
                    raise ParsingError('Already know section %r from %r.' 
                                       % (section.name, sections[section.name].where),
                                       el.where)
                sections[section.name] = section
                
                if parent:
                    sections[parent].subs[section.name] = section
                     
                current_section = section
                yield current_section
        elif isinstance(el, OtherLine):
            yield el
        else: assert False

def main():
    for cmd in parse_symbols(sys.stdin, 'stdin'):
        print(cmd)

if __name__ == '__main__':
    main()
    
