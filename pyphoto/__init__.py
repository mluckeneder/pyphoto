"""pyPhoto
"""
from __future__ import absolute_import

__version__ = "0.0.5"

import logging
import colorama
colorama.init()

def setup_custom_logger(name=""):
    """creates custom logger"""
    formatter = logging.Formatter(
        fmt='%(asctime)s - '+colorama.Fore.RED+'%(levelname)s'+colorama.Fore.RESET+' - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

logger = setup_custom_logger()


from .iphoto_library import IPhotoLibrary
from .flickr_uploader import FlickrUploader
from .main_program import MainProgram
from .pyphoto_exception import PyPhotoException
from .retrier import retrier
