from optparse import OptionParser
from . import find_all_commands
import yaml

usage = """ 

    %cmd <file>
    
Collects all symbols used by the TeX file and its children.
"""


def main():
    parser = OptionParser(usage)
    #    parser.add_option("--style", help="Type of table", default='full')
    (options, args) = parser.parse_args() #@UnusedVariable
    filenames = args

    symbols = set()
    for filename in filenames:
        symbols.update(find_all_commands(filename))
    what = list(symbols)
    print('# YAML dump of symbols found in files %s' % filenames)
    print('# ')
    print(yaml.dump(what))

if __name__ == '__main__':
    main()

