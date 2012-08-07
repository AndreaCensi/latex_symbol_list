import re
import os
import glob
 
file_pattern = '*.tex'
include_pattern = '\\input{(.*?)}'

def tex_deps_all_main():
    for lyx_file in glob.glob(file_pattern):
        base = os.path.splitext(lyx_file)[0]
        deps = get_deps_recursive(lyx_file)        
        print('%s.pdf: %s.tex %s' % (base, base, " ".join(deps)))

def get_deps_recursive(lyx_file, found=None):
    if found == None:
        found = []
    if lyx_file in found:
        return []
    found.append(lyx_file)
    deps = get_deps(lyx_file)
    for x in list(deps):
        if not x in found:
            found.append(x)
            deps.extend(get_deps_recursive(lyx_file, found))
    return deps
    
def get_deps(lyx_file):
    regex = re.compile(include_pattern)
    
    deps = []
    for line in open(lyx_file):
        for x in regex.findall(line):
            deps.append(x)
    deps = list(set(deps))
    return deps
    
if __name__ == '__main__':
    tex_deps_all_main()
