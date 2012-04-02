from .. import logger, parse_all_sections_symbols
from optparse import OptionParser
import sys
import yaml


def main():
    parser = OptionParser()
    parser.add_option("--only", help="YAML file containing the symbols"
                      "that must be included.")

    (options, args) = parser.parse_args() #@UnusedVariable

    sections, symbols = parse_all_sections_symbols(args)
    logger.info('Loaded %d sections with %d symbols.\n' %
                (len(sections), len(symbols)))
    if not sections or not symbols:
        raise Exception('Not enough data found.')

    if options.only:
        with open(options.only) as f:
            only = yaml.load(f)

        have = set(symbols.keys())
        used = set(only)
        have_but_not_used = have.difference(used)
        used_but_not_have = used.difference(have)
        logger.info('have: %s' % have)
        logger.info('used: %s' % used)
        logger.info('have_but_not_used: %s' % have_but_not_used)
        logger.info('used_but_not_have: %s' % used_but_not_have)
        have_and_used = have.intersection(used)
        symbols = dict((k, v) for k, v in symbols.items()
                       if k in have_and_used)
    else:
        only = None

    print_nomenclature(symbols, sys.stdout, skip_empty=False)


def print_nomenclature(symbols, stream, skip_empty=True):
    for symbol in symbols.values():
        if 'nomenc-exclude' in symbol.other:
            stream.write('%% Skipping symbol %s because of '
                         'nomenc-exclude\n' % symbol)
            continue

        if symbol.nomenclature is None:
            if skip_empty:
                stream.write('%% Skipping symbol %s\n' % symbol)
                continue

            if symbol.nargs != 0:
                stream.write('%% Skipping symbol %s because it has args\n'
                              % symbol)
                continue

            text = symbol.desc
            label = '$%s$' % symbol.symbol
        else:
            text = symbol.nomenclature.text
            label = symbol.nomenclature.label
            label = '$%s$' % label

        ref = symbol.other.get('def', None)
        if ref:
            text += ' \\nomencref{%s}' % ref

        if not 'sort' in symbol.other:
            sort_options = ''
        else:
            sort_options = '[a%s]' % symbol.other['sort']

        s = r'\nomenclature%s{%s}{%s}' % (sort_options, label, text)
        stream.write(s)
        stream.write('\n')

if __name__ == '__main__':
    main()

