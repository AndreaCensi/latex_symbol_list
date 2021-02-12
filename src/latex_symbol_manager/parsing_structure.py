import sys

from . import (
    KNOWN_TAGS_SECTIONS,
    KNOWN_TAGS_SYMBOLS,
    logger,
    Lookahead,
    NewCommand,
    NomenclatureEntry,
    OtherLine,
    parse_stream,
    ParsingError,
    SpecialComment,
    Symbol,
    SymbolSection,
)


def warning(s, el=None):
    if el:
        logger.warn("Warning: %s\n @ %s" % (s, el.where))
    else:
        logger.warn("Warning: %s" % s)


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
            if el.tag == "section":
                if not ":" in el.lines[0] or len(el.lines) > 1:
                    err = "Malformed section tag: {0!r}".format(el)
                    raise ParsingError(err, el.where)
                name, description = el.lines[0].split(":")
                name = name.strip()
                description = description.strip()
                current_section = create_section(el, peek, sections, name, description)
                yield current_section
            else:
                warning("Floating line", el)

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
            err = "Already know section %r from %r." % (name, sections[name].where)
            raise ParsingError(err, el.where)

    # Check subs
    if "/" in name:
        parent = name.split("/")[0].strip()
        if not parent in sections:
            if False:  # tmp disable
                warning(
                    "Creating dummy parent section %r.\n "
                    "Already know %s." % (parent, list(sections.keys())),
                    el,
                )
            create_section(el, None, sections, parent, "")
    else:
        parent = None

    if peek is not None:
        attrs = load_attributes(peek, KNOWN_TAGS_SECTIONS)
    else:
        attrs = {}

    definition_order = len(sections)

    section = SymbolSection(
        name, description, {}, parent, {}, el.where, definition_order, attrs
    )
    sections[section.name] = section

    if parent is not None:
        sections[parent].subs[section.name] = section

    return section


def load_command(peek, el, current_section, symbols):
    if current_section is None:
        err = "No section defined yet"
        raise ParsingError(err, el.where)

    other = load_attributes(peek, KNOWN_TAGS_SYMBOLS)

    if "todo" in other:
        logger.warn("TODO (%s): %s" % (el.command, other["todo"]))

    if "nomenc" in other:
        parts = other["nomenc"].split(":")
        if len(parts) != 2:
            err = "Too many elements in %r" % other["nomenc"]
            raise ParsingError(err, el.where)
        label, text = parts
        nomenc = NomenclatureEntry(label, text)
    else:
        nomenc = None

    example = other.get("example")

    tag = current_section.name

    if el.command in symbols:
        err = "Already know symbol %r from %r." % (
            el.command,
            symbols[el.command].where,
        )
        raise ParsingError(err, el.where)

    # merge attributes from section
    for k, v in list(current_section.attrs.items()):
        ok_to_disagree = ["def"]
        if k in other and other[k] != v and not k in ok_to_disagree:
            warning(
                "Note: tag %r = %r disagrees with section (%r)" % (k, other[k], v), el
            )
        else:
            other[k] = v

    definition_order = len(symbols)
    s = Symbol(
        el.command,
        definition_order=definition_order,
        tex=el.body,
        desc=el.comment,
        tag=tag,
        # int=None,
        example=example,
        nargs=el.nargs,
        where=el.where,
        nomenclature=nomenc,
        other=other,
    )
    symbols[el.command] = s
    current_section.symbols[el.command] = s
    return s


def load_attributes(peek, known, stop_on=["section"]):
    attrs = {}
    while isinstance(peek.lookahead(0), SpecialComment) and not (
        peek.lookahead(0).tag in stop_on
    ):
        sc = next(peek)
        if not sc.tag in KNOWN_TAGS_SYMBOLS:
            warning("Found strange tag %r." % sc.tag, sc)
        if sc.tag in attrs:
            warning("Overwriting tag %r." % sc.tag, sc)
        attrs[sc.tag] = " ".join(sc.lines).strip()
    return attrs


def main():
    for cmd in parse_symbols(sys.stdin, "stdin"):
        print(cmd)


if __name__ == "__main__":
    main()
