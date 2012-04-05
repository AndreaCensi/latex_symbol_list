from . import (NewCommand, OtherLine, SpecialComment, SymbolSection,
    logger, ParsingError, Lookahead, NomenclatureEntry, Symbol, parse_stream)
import sys


def parse_symbols(stream, filename, sections=None, symbols=None):
    current_section = None
    if sections is None:
        sections = {}
    if symbols is None:
        symbols = {}

    def create_section(name, description):
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
                msg = 'Could not find parent section %r. ' % parent
                sys.stderr.write("warning: %s\n" % msg)
                sys.stderr.write('     at: %s\n' % el.where)
                create_section(parent, name)
        else:
            parent = None

        definition_order = len(sections)

        section = SymbolSection(name, description,
                                {}, parent, {}, el.where, definition_order)
        sections[section.name] = section

        if parent is not None:
            sections[parent].subs[section.name] = section

        return section

    peek = Lookahead(parse_stream(stream, filename))

    for el in peek:
        if isinstance(el, NewCommand):
            if current_section is None:
                err = 'No section defined yet'
                raise ParsingError(err, el.where)

            example = None
            nomenc = None
#            sorting = None
            other = {}

            while (isinstance(peek.lookahead(0), SpecialComment) and
                not(peek.lookahead(0).tag == 'section')):
                sc = peek.next()
                if sc.tag == 'example':
                    example = "\n".join(sc.lines)
#                elif sc.tag == 'sort':
#                    sorting = " ".join(sc.lines).strip()
                elif sc.tag == 'nomenc':
                    content = " ".join(sc.lines)
                    label, text = content.split(':')
                    nomenc = NomenclatureEntry(label, text)
                else:
                    logger.info('found extra %s' % sc.tag)
                    # xxx: check not already
                    other[sc.tag] = " ".join(sc.lines).strip()
#                    msg = 'Unknown tag %r' % sc.tag
#                    raise ParsingError(msg, sc.where)

            tag = current_section.name

            if el.command in symbols:
                err = ('Already know symbol %r from %r.' %
                        (el.command, symbols[el.command].where))
                raise ParsingError(err, el.where)

            definition_order = len(symbols)
            s = Symbol(el.command, definition_order=definition_order,
                        tex=el.body, desc=el.comment, tag=tag,
                       long=None, example=example, nargs=el.nargs,
                       where=el.where, nomenclature=nomenc,
                       #sorting=sorting,
                       other=other)
            symbols[el.command] = s
            current_section.symbols[el.command] = s

            yield s

        elif isinstance(el, SpecialComment):
            if el.tag == 'section':
                if not ':' in el.lines[0] or len(el.lines) > 1:
                    err = 'Malformed section tag: {0!r}'.format(el)
                    raise ParsingError(err, el.where)
                name, description = el.lines[0].split(':')
                name = name.strip()
                description = description.strip()
                section = create_section(name, description)

                current_section = section
                yield current_section
        elif isinstance(el, OtherLine):
            yield el
        else: assert False

def main():
    for cmd in parse_symbols(sys.stdin, 'stdin'):
        print(cmd)

if __name__ == '__main__':
    main()

