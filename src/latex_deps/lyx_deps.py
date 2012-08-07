import sys
import re

usage = """

    lyx-deps  <file1.lyx> ...
    
    
Greps the lines with format:

filename "*.lyx" 
"""

def lyx_deps_main():
    files = sys.argv[1:]
    if not files:
        return
    
    pattern = 'filename "(.*?)"'
    regex = re.compile(pattern)
    
    deps = []
    for f in files:
        for line in open(f):
            for x in regex.findall(line):
                deps.append(x)

    deps = list(set(deps))
    print(" ".join(deps))
    
if __name__ == '__main__':
    lyx_deps_main()
