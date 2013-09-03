from __future__ import absolute_import
from .pyphoto_exception import PyPhotoException
from urllib2 import HTTPError, URLError
from functools import wraps
import logging


LOG = logging.getLogger()


def retrier(func, retries=5):
    """makes an api call retry several times before failing"""
    # @wraps(func)
    def wrapper(*args, **kwargs):
        counter = 0
        retval = None
        while counter < retries:
            counter += 1
            try:
                retval = func(*args, **kwargs)
                break
            except PyPhotoException as err:
                LOG.debug("Retrying after error %s" % (err.message))
                continue
            except HTTPError as http_error:
                if http_error.code in [504, 400, 500]:
                    LOG.debug("Retrying after error %i" % (http_error.code))
                    continue
                else:
                    raise http_error
            except URLError as err:
                LOG.debug("Retrying after URLError")
                continue

            # except BaseException as err:
                # LOG.debug("Retrying after exception %s" % (err.message))
                # continue

        return retval

    return wrapper
