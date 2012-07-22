import sys, yaml, os, glob

import logging
logging.basicConfig()
logger = logging.getLogger(__name__) # XXX
logger.setLevel(logging.INFO)

class UserError(Exception):
    pass


def wrap_script(entry):
    try:
        entry(sys.argv)
    except UserError as e:
        logger.error(e)
        sys.exit(-2)