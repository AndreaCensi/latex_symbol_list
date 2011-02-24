from latex_symbol_manager.parsing_structure import parse_symbols
import sys
from latex_symbol_manager.structures import OtherLine, ParsingError, \
    SymbolSection
from latex_symbol_manager.symbol import Symbol

from optparse import OptionParser

def main(): 
    
    parser = OptionParser()
    
    parser.add_option("--highlight", help="Highlight use of known symbols", default=False, action='store_true')
            
    (options, args) = parser.parse_args() #@UnusedVariable


    for el in parse_symbols(sys.stdin, 'stdin'): #@UnusedVariable
        if isinstance(el, OtherLine):
            sys.stdout.write(el.line)
            sys.stdout.write('\n')
        elif isinstance(el, Symbol):
            if options.highlight and el.nargs == 0:
                wrapper = lambda x: "{\\color[rgb]{0,0.5,0} %s}" % x
            else:
                wrapper = lambda x: x

            sys.stdout.write(el.tex_definition(wrapper=wrapper))
            sys.stdout.write('\n')
        elif isinstance(el, SymbolSection):
            pass
        else:
            raise ParsingError('Unknown element: {0}'.format(el), el.where)
            assert False 
    
if __name__ == '__main__':
    main()

