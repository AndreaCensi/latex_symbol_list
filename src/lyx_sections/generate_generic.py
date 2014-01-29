import glob

from lyx_sections.generate_generic_templates import inset_template, templates
from lyx_sections.misc_utils import UserError
from lyx_sections.subst import substitute

from . import logger


def generate(pattern, entry2value,
                           template_main=templates['amsbook'],
                           template_inset=inset_template,
                           exclude=[]):

    main = generate_index(pattern, entry2value,
                          template_main,
                          template_inset,
                          exclude)
    print(main)


def generate_index(pattern, entry2value,
                           template_main=templates['amsbook'],
                           template_inset=inset_template,
                           exclude=[],
                           preamble=''):
    chapters = list(glob.glob(pattern))

    for e in exclude:
        if e in chapters:
            logger.debug('Removing %s' % e)
            chapters.remove(e)

    if not chapters:
        raise UserError('Could not find any chapter matching %r' 
            % pattern)

    logger.info('Found %d: %s ' % (len(chapters), chapters))

    chapters = sorted(chapters)
    main = create_lyx_file(chapters, entry2value, template_main, template_inset,
                           preamble=preamble)
    logger.debug('Done.')
    return main

def create_lyx_file(chapters, entry2value, template_main, template_inset,
                    preamble=''):
    """ Returns a string with the template """
    insets = ''
    for chap in chapters:
        filename = entry2value(chap) 
        inset = substitute(template_inset, filename=filename)
        insets += inset 

    main = substitute(template_main, content=insets, preamble=preamble)
    return main


