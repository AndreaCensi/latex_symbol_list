from latex_symbol_manager.parsing_structure import parse_symbols
import sys

example_size = '9cm'

def create_table(sections, output, write_examples=True):
    output.write("""
\\begin{longtable}{cll}
    Symbol & \\TeX command & description \\\\
    \\hline \\hline
""")
    
    def write_table_line(t):
        output.write(" & ".join(t) + '\\\\ \n')
        
    for section in sections:
        if section.parent:
            parent = 'parent: %s' % section.parent
        else: parent = ''
        
        write_table_line(['', '', ''])
        
        output.write('%s & \multicolumn{2}{|l|}{%s} \\\\ \n' % 
                     (section.name, section.description))
#        write_table_line((section.name, parent, ''))
        output.write('\\hline\n')
        if section.parent is None:
            output.write('\\hline\n')
            
        symbols = [v for k, v in section.symbols.items()] #@UnusedVariable
        symbols.sort(key=lambda v:v.symbol.lower())
        for s in symbols:
            
            if s.nargs == 0:
                write_table_line(['$%s$' % s.symbol,
                              '\\texttt{\\textbackslash{}%s}' % s.symbol[1:],
                              s.desc])
            else:
                args = ",".join(['\dots'] * s.nargs)
                write_table_line(['',
                              '\\texttt{\\textbackslash{}%s\{%s\}}' % (s.symbol[1:], args),
                              s.desc])
            if s.example and write_examples:
                ex = ('\\begin{minipage}{%s}\\color[rgb]{0.5,0.5,0.5}%%\n%s%%\n\end{minipage}' 
                      % (example_size, s.example))
                write_table_line(['', '', ex])
    
    
    output.write("""\\end{longtable} """)


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

