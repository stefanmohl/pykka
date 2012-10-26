# flake8: noqa
from pykka.exceptions import ActorDeadError, Timeout


#: Pykka's :pep:`386` and :pep:`396` compatible version number
__version__ = '0.16'


#: Pykka's version as a tuple that can be used for comparison
#:
#: .. deprecated:: 0.14
#:    Use :attr:`__version__` instead. This will be removed in a future
#:    release.
VERSION = tuple(map(int, __version__.split('.')))


def get_version():
    """
    Returns Pykka's version as a formatted string

    .. deprecated:: 0.14
       Use :attr:`__version__` instead. This will be removed in a future
       release.
    """
    return __version__


def _add_null_handler_for_logging():
    import logging
    try:
        NullHandler = logging.NullHandler  # Python 2.7 and upwards
    except AttributeError:
        class NullHandler(logging.Handler):
            def emit(self, record):
                pass
    logging.getLogger('pykka').addHandler(NullHandler())

_add_null_handler_for_logging()
