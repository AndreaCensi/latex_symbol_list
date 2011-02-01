import re, sys
from .structures import NewCommand, OtherLine, \
    SpecialComment, ParsingError, Where

from .lookahead import Lookahead
    
def strip_empty(stream):
    for line in stream: #@UnusedVariable
        if line is not None:
            # and line.strip():
            yield line
            
def count_lines(stream, count=0):
    count_lines.count = count
    for line in stream:
        yield line
        count_lines.count += 1
            
def is_comment(line): 
    return bool(line.lstrip().startswith('%'))

def is_special_comment(line): 
    return bool(line.lstrip().startswith('%:'))
    
    
    
def parse_stream(stream, filename, line_count=0):
    ''' 
        Parses a tex stream line-by-line and returns objects
        of the kind NewCommand, SpecialComment, OtherLine.
    '''
    
    counter = count_lines(stream, line_count)
    peek = Lookahead(strip_empty(counter))
    
    for line in peek:
        where = Where(filename, count_lines.count, line)
        m = re.match(r'\s*\\newcommand{\\(\w+)}{(.*)}\s*%?(.*)', line)
        if m:
            symbol = '\\' + m.group(1)
            command = m.group(2)
            description = m.group(3)
            description = description.replace('%', '') 
            yield NewCommand(symbol, 0, command, description, where)
        else:
            m = re.match(r'\s*\\newcommand{\\(\w+)}\[(\d*)\]{(.*)}\s*%?(.*)', line)
            if m:
                symbol = '\\' + m.group(1)
                nargs = int(m.group(2))
                command = m.group(3)
                description = m.group(4)
                description = description.replace('%', '') 
                yield NewCommand(symbol, nargs, command, description, where)
        
            elif is_special_comment(line):
                rest = line[line.index('%:') + 2:]
                if not ':' in rest:
                    raise ParsingError('No closing ":" found.', where)
                pos = rest.index(':')
                tag = rest[:pos]
                lines = [ rest[pos + 1:]]
                
                while peek.lookahead(0) and is_comment(peek.lookahead(0)):
                    lines.append(peek.next())
        
                yield SpecialComment(tag, lines, where)
            else:
                yield OtherLine(line, where)

def main():
    for cmd in parse_stream(sys.stdin, 'stdin'):
        print(cmd)

if __name__ == '__main__':
    main()
    
    
    
    
