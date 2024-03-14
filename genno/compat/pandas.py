import logging
from contextlib import contextmanager

log = logging.getLogger(__name__)


@contextmanager
def disable_copy_on_write(name):
    """Context manager to disable pandas copy-on-write."""
    import pandas

    stored = pandas.options.mode.copy_on_write
    override_value = "warn" if pandas.__version__ >= "2.2.0" else False

    try:
        if stored is True:
            log.debug(f"Override pandas.mode.options.copy_on_write = True for {name}")
            pandas.options.mode.copy_on_write = override_value
        yield
    finally:
        pandas.options.mode.copy_on_write = stored
