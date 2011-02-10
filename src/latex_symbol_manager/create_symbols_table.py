import sys

from latex_gen import (color_rgb, small, verbatim_soft,
    fbox, hspace, minipage, latex_escape, texttt)

from .parsing_structure import parse_symbols
from latex_gen import latex_fragment


example_size = '9cm'

def write_symbol_rows(s, table, write_examples):
    if s.nargs == 0:
        with table.row() as row:
            row.cell_tex('$%s$' % s.symbol)
            row.cell_tex(texttt(latex_escape(s.symbol)))
            row.cell_tex(s.desc)
    else:
        args = ",".join(['...'] * s.nargs)
        example = '%s{%s}' % (s.symbol, args)
        with table.row() as row:
            row.cell_tex(texttt(latex_escape(example)))
            row.cell_tex(texttt(latex_escape(example)))
            row.cell_tex(s.desc)
        
    if s.example and write_examples:
        
        with table.row() as row:
            row.cell_tex()
            row.cell_tex()
            with row.cell() as cell:
                cell.hspace('2cm')
                
                with cell.fbox() as box:
                    box.color(0.5, 0.5, 0.5)
                    with box.minipage(example_size) as mp:
                        mp.tex(s.example)
                        mp.parbreak()
                        mp.tex(small(verbatim_soft(s.example)))
            
def create_table(sections, output, write_examples=True):
    
    with latex_fragment(output) as fragment:
        with fragment.longtable(['c', 'l', 'l']) as table:
            
            table.row_tex('Symbol', '\\TeX command', 'description')
            table.hline()
            table.hline() 
                
            for section in sections:
                table.row_tex('', '', '')
                
                with table.row() as row:
                    row.cell_tex(latex_escape(section.name))
                    row.multicolumn_tex(2, 'l', section.description)
                
                table.hline()
                if section.parent is None: 
                    table.hline()
                    
                symbols = [v for k, v in section.symbols.items()] #@UnusedVariable
                symbols.sort(key=lambda v:v.symbol.lower())
                for s in symbols:
                    write_symbol_rows(s, table, write_examples)
                    
                    
 

def main():
    sections = {}
    symbols = {} 
    for cmd in parse_symbols(sys.stdin, 'stdin', sections, symbols): #@UnusedVariable
        pass

    sys.stderr.write('Loaded %d sections with %d symbols.\n' % (len(sections),
                                                             len(symbols)))
    if not sections or not symbols:
        sys.stderr.write('Not enough data found.\n')
        sys.exit(-1)
        
    which = sys.argv[1:]
    if which:
        selected = dict([(k, v) for (k, v) in sections.items() if k in which])
    else:
        selected = sections
        
    ordered = [v for k, v in selected.items()]
    ordered.sort(key=lambda v:v.name)
    create_table(ordered, sys.stdout, write_examples=True) 
    
    
if __name__ == '__main__':
    main()

