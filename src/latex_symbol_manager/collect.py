from collections import defaultdict
from optparse import OptionParser
from typing import Dict, List

import yaml
from zuper_ipce import IESO, ipce_from_object

from .find_commands import find_all_commands, Usage

usage = """ 

    %cmd <file>
    
Collects all symbols used by the TeX file and its children.
"""


def main():
    parser = OptionParser(usage)
    #    parser.add_option("--style", help="Type of table", default='full')
    (options, args) = parser.parse_args()  # @UnusedVariable
    filenames = args

    filenames = sorted(filenames)
    symbols: Dict[str, List[Usage]] = defaultdict(list)
    for filename in filenames:
        fs = find_all_commands(filename)
        for k, v in fs.items():
            symbols[k].extend(v)
    # print(symbols)
    # what = list(symbols)

    print(("# YAML dump of symbols found in files %s" % filenames))
    print("# ")
    # print((yaml.dump(what)))

    a = ipce_from_object(symbols, ieso=IESO(False, False))
    print((yaml.dump(a)))


if __name__ == "__main__":
    main()
