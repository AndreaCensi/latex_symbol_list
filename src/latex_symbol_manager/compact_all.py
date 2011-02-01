from latex_symbol_manager.parsing_structure import parse_symbols
import sys
from latex_symbol_manager.structures import OtherLine, ParsingError, \
    SymbolSection
from latex_symbol_manager.symbol import Symbol

def main(): 
    for el in parse_symbols(sys.stdin, 'stdin'): #@UnusedVariable
        if isinstance(el, OtherLine):
            sys.stdout.write(el.line)
            sys.stdout.write('\n')
        elif isinstance(el, Symbol):
            sys.stdout.write(el.tex_definition())
            sys.stdout.write('\n')
        elif isinstance(el, SymbolSection):
            pass
        else:
            raise ParsingError('Unknown element: {0}'.format(el), el.where)
            assert False 
    
if __name__ == '__main__':
    main()

