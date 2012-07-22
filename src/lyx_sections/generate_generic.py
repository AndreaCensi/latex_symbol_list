from . import *

def generate(pattern,                             entry2value,
                           template_main=lyx_template, 
                           template_inset=inset_template,exclude=[]):
    chapters = list( glob.glob(pattern) )

    for e in exclude:
        if e in chapters:
            logger.debug('Removing %s' % e)
            chapters.remove(e)

    if not chapters:
        raise UserError('Could not find any chapter matching %r' 
            % pattern)

    logger.debug('Found %d subs. ' % len(chapters))

    chapters = sorted(chapters)
    main = create_lyx_file(chapters, entry2value, template_main, template_inset)
    print(main)

    logger.debug('Done.')

def create_lyx_file(chapters, entry2value, template_main, template_inset):
    """ Returns a string with the template """
    insets = ''
    for chap in chapters:
        filename=entry2value(chap) 
        inset = substitute(template_inset, filename=filename)
        insets += inset 

    main = substitute(template_main, content=insets)
    return main


