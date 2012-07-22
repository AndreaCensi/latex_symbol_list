#!/usr/bin/env python
import sys
import re
import os
import glob

import logging
logging.basicConfig()
logger = logging.getLogger('L')
logger.setLevel(logging.INFO)


def lyx_deps_all_main():
    roots = sys.argv[1:]
    if not roots:
        roots = list(glob.glob('*.lyx'))
    logger.debug('roots: %r' %roots)
    for lyx_file in roots:
        base = os.path.splitext(lyx_file)[0]
        deps = get_deps_recursive(lyx_file)        
        print('%s.tex: %s.lyx %s' % (base, base, " ".join(deps)))
        print('%s.lyx.d: %s.lyx %s' % (base, base, " ".join(deps)))

Cache = {}
stack = []
def get_deps_recursive(lyx_file):
    lyx_file = os.path.realpath(lyx_file)
    if lyx_file in Cache:
        return Cache[lyx_file]
    if lyx_file in stack:
            raise Exception('%r found again; stack %r' % (lyx_file, stack))
    stack.append(lyx_file)

    deps = list(get_deps(lyx_file))
    
    #print("%s: %s %s" % ( '** ' * len(stack), lyx_file, deps))
#    logger.debug('for %r: 1 level %s' % (lyx_file, deps))

    alldeps = []
    alldeps.extend(deps)
    for x in deps:
        if os.path.exists(x):
            alldeps.extend(get_deps_recursive(x))
        else:
            logger.warning('Path not existing (%s)' % x)
        
#    logger.debug('for %r: %s' % (lyx_file, deps))
    
    stack.pop()
    Cache[lyx_file] = alldeps
    return alldeps


# def get_deps_recursive(lyx_file, found=None):
#     if found == None:
#         found = []
#     if lyx_file in found:
#         return []
#     found.append(lyx_file)
#     deps = get_deps(lyx_file)
#     for x in list(deps):
#         if not x in found:
#             found.append(x)
#             deps.extend(get_deps_recursive(lyx_file, found))
#     logger.debug('for %r: %s' % (lyx_file, deps))
#     return deps
    
def get_deps(lyx_file):
    pattern = 'filename "(.*?)"'
    regex = re.compile(pattern)
    
    deps = []
    for line in open(lyx_file):
        for x in regex.findall(line):
            path = os.path.join(os.path.dirname(lyx_file), x)
            deps.append(path)
    deps = list(set(deps))
    return deps
    
if __name__ == '__main__':
    lyx_deps_all_main()
