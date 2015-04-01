'''Docstring'''

import os
import logging


def setup_logger(path="./system.log", level=logging.DEBUG, depr_warnings=False,
        log_format=None):
    """Sets up the logger as a standard Python logger.

    Defines a logging format and if the system is setup in development mode,
    adds system warnings (such as use of deprecated methods, etc).

    """
    if not log_format:
        log_format = ('%(asctime)-15s %(levelname)-8s %(message)s '
            '[%(name)s:line=%(lineno)s]')
    directories, _ = os.path.split(path)
    if not os.path.isdir(directories):
        os.makedirs(directories)
    logging.basicConfig(level=level, format=log_format,
        filename=path, filemode='a')
    if depr_warnings == True:
        import warnings
        warnings.simplefilter('default')
        logging.captureWarnings(True)
