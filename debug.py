#
# Debugging utilities
#

from time import time
import logging
from contextlib import contextmanager


def enable_db_logging():
    """
    Enable database logging.  Useful in Djanjo shell.
    """
    logger = logging.getLogger('django.db.backends')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


# Wrap a block a code to display wall clock execution
# time.

@contextmanager
def timing(label: str, indent: int = 0) -> None:
    start = time()
    yield
    elapsed = time() - start
    spaces = ' ' * indent
    print(f"{spaces}{label}: {elapsed:.2f} secs")
