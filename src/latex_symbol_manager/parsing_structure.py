from . import (NewCommand, OtherLine, SpecialComment, SymbolSection,
    logger, ParsingError, Lookahead, NomenclatureEntry, Symbol, parse_stream)
import sys


def warning(s, el=None):
    if el:
        logger.warn('Warning: %s\n @ %s' % (s, el.where))
    else:
        logger.warn('Warning: %s' % s)


def parse_symbols(stream, filename, sections=None, symbols=None):
    current_section = None
    if sections is None:
        sections = {}
    if symbols is None:
        symbols = {}

    peek = Lookahead(parse_stream(stream, filename))

    for el in peek:
        if isinstance(el, NewCommand):
            yield load_command(peek, el, current_section, symbols)

        elif isinstance(el, SpecialComment):
            if el.tag == 'section':
                if not ':' in el.lines[0] or len(el.lines) > 1:
                    err = 'Malformed section tag: {0!r}'.format(el)
                    raise ParsingError(err, el.where)
                name, description = el.lines[0].split(':')
                name = name.strip()
                description = description.strip()
                current_section = create_section(el, peek, sections,
                                                 name, description)
                yield current_section
            else:
                warning('Floating line', el)

        elif isinstance(el, OtherLine):
            yield el
        else:
            assert False


def create_section(el, peek, sections, name, description):
    if name in sections:
        if sections[name].description is None:
            # if it was temporary
            sections[name].description = description
            return name
        else:
            err = ('Already know section %r from %r.'
                    % (name, sections[name].where))
            raise ParsingError(err, el.where)

    # Check subs
    if '/' in name:
        parent = name.split('/')[0].strip()
        if not parent in sections:
            warning('Creating dummy parent section %r. ' % parent, el)
            create_section(el, None, sections, parent, '')
    else:
        parent = None

    if peek is not None:
        attrs = load_attributes(peek, KNOWN_TAGS_SECTIONS)
    else:
        attrs = {}

    definition_order = len(sections)

    section = SymbolSection(name, description,
                            {}, parent, {}, el.where,
                            definition_order, attrs)
    sections[section.name] = section

    if parent is not None:
        sections[parent].subs[section.name] = section

    return section


def load_command(peek, el, current_section, symbols):

    if current_section is None:
        err = 'No section defined yet'
        raise ParsingError(err, el.where)

    other = load_attributes(peek, KNOWN_TAGS_SYMBOLS)

    if 'nomenc' in other:
        label, text = other['nomenc'].split(':')
        nomenc = NomenclatureEntry(label, text)
    else:
        nomenc = None

    example = other.get('example')

    tag = current_section.name

    if el.command in symbols:
        err = ('Already know symbol %r from %r.' %
                (el.command, symbols[el.command].where))
        raise ParsingError(err, el.where)

    # merge attributes from section
    for k, v in  current_section.attrs.items():
        if k in other and other[k] != v:
            warning('Overwriting tag %r = %r with section value (%r)'
                    % (k, other[k], v), el)
        other[k] = v

    definition_order = len(symbols)
    s = Symbol(el.command, definition_order=definition_order,
               tex=el.body, desc=el.comment, tag=tag,
               long=None, example=example, nargs=el.nargs,
               where=el.where, nomenclature=nomenc,
               other=other)
    symbols[el.command] = s
    current_section.symbols[el.command] = s
    return s


KNOWN_TAGS_SYMBOLS = ['def', 'nomenc', 'nomenc-exclude',
              'sort', 'notfinal', 'deprecated', 'example']
KNOWN_TAGS_SECTIONS = ['nomenc-exclude', 'notfinal', 'deprecated']


def load_attributes(peek, known, stop_on=['section']):
    attrs = {}
    while (isinstance(peek.lookahead(0), SpecialComment) and
        not(peek.lookahead(0).tag in stop_on)):
        sc = peek.next()
        if not sc.tag in KNOWN_TAGS_SYMBOLS:
            warning('Found strange tag %r.' % sc.tag, sc)
        if sc.tag in attrs:
            warning('Overwriting tag %r.' % sc.tag, sc)
        attrs[sc.tag] = " ".join(sc.lines).strip()

    return attrs


def main():
    for cmd in parse_symbols(sys.stdin, 'stdin'):
        print(cmd)

if __name__ == '__main__':
    main()

