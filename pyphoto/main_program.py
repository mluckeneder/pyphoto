"""Main program"""

from __future__ import absolute_import

import logging
from .iphoto_library import IPhotoLibrary
from .flickr_uploader import FlickrUploader
import pyphoto

LOG = logging.getLogger()


class MainProgram(object):
    """Main Program script"""

    def __init__(self, iphoto, **kwargs):
        self.iphoto = iphoto
        if kwargs["flickr_key"] and kwargs["flickr_secret"]:
            self.flickr_api_key = kwargs["flickr_key"]
            self.flickr_api_secret = kwargs["flickr_secret"]
        else:
            import config
            self.flickr_api_key = config.API_KEY
            self.flickr_api_secret = config.API_SECRET

        self.uploader = None
        self.library = None

    def run(self):
        """Run the main program"""
        LOG.info("Loaded program v%s" % (pyphoto.__version__))

        # TODO validate
        self.library = IPhotoLibrary(self.iphoto)
        uploader = FlickrUploader(flickr_key=self.flickr_api_key,
            flickr_secret=self.flickr_api_secret)

        self.library.upload_files(uploader)
