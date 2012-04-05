from .. import logger, parse_all_sections_symbols
from ..utils import wrap_script_entry_point
from optparse import OptionParser
import sys
import yaml


def nomenc_main(args):
    parser = OptionParser()
    parser.add_option("--only", help="YAML file containing the symbols"
                      "that must be included.")

    (options, args) = parser.parse_args(args) #@UnusedVariable

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
    def warn(s):
        stream.write('%% %s\n' % s)
        logger.warn(s)

    for symbol in symbols.values():
        if 'nomenc-exclude' in symbol.other:
            warn('Skipping symbol %s because of '
                         'nomenc-exclude' % symbol.symbol)
            continue

        if symbol.nomenclature is None:
            if skip_empty:
                warn('Skipping symbol %s because of skip_empty.' %
                     symbol.symbol)
                continue

            if symbol.nargs != 0:
                warn('Skipping symbol %s because it has args.' %
                     symbol.symbol)
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

        ADDPREFIX = 'symbols'
        if not 'sort' in symbol.other:
            sort_options = '[%s]' % (ADDPREFIX)
        else:
            sort_options = '[%s%s]' % (ADDPREFIX, symbol.other['sort'])

        text = text.strip()
        if not text:
            warn('No text for %s' % symbol.symbol)
            text = '\\texttt{%s}' % symbol.symbol[1:]
        s = r'\nomenclature%s{%s}{%s}' % (sort_options, label, text)

        stream.write(s)
        stream.write('\n')


def main():
    wrap_script_entry_point(nomenc_main, logger)

if __name__ == '__main__':
    main()
