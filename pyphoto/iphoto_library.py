"""
    pyphoto.iphoto_library
    ~~~~~~~~~~~~~~~~

    Accesses an iPhoto Library file.

    :copyright: (c) 2013 by Michael Luckeneder.
"""
from __future__ import absolute_import
from .pyphoto_exception import PyPhotoException

import logging
import plistlib
import os
import unicodedata


LOG = logging.getLogger()


class IPhotoLibrary(object):
    """represents the iPhoto library on disk"""


    def __init__(self, librarypath):
        LOG.debug("Loaded iPhoto Library class")
        self._librarypath = librarypath
        self._plist = None
        self.events = None
        self.master_images = None
        self.pyphoto_setid = None


        # validate iPhoto library
        self._validate_iphoto_library()


        # parse plist file to extract information
        self._parse_plist()

        if not self._validate_iphoto_library_version():
            raise PyPhotoException("Unsupported Version")


    def _parse_plist(self):
        """parse a plist iPhoto library file"""
        try:
            LOG.debug("parsing plist file")

            # read events and master images
            self._plist = plistlib.readPlist(self._make_path("AlbumData.xml"))
            self.events = self._plist["List of Rolls"]
            self.master_images = self._plist["Master Image List"]
        except Exception, ex:
            raise Exception(ex.message)

    def get_list_of_master_files(self):
        """extracts (GUID, path) dict of master images"""

        LOG.debug("retrieving list of master files")
        return dict((p["GUID"].encode("utf-8"),
                        p.get("OriginalPath", p["ImagePath"]).encode("utf-8"))
                    for p in self.master_images.values())

    def join_events_with_masters(self):
        """generate events with nested masters
           :return: dict()
        """
        LOG.debug("joining events with masters")
        events = {}

        # iterate over events
        for event in self.events:
            images = {}
            # iterate over image keys
            for photo in event["KeyList"]:
                master = self.master_images[photo]
                guid = master["GUID"].encode("utf-8")
                images[guid] = master.get("OriginalPath",
                    master["ImagePath"]).encode("utf-8")

            # assign event a list of images
            events[event["RollName"].encode("utf-8")] = images

        return events

    def _make_path(self, *paths):
        """makes path relative to library path"""
        return os.path.join(self._librarypath, *paths)

    def _validate_iphoto_library_version(self):
        """validates if iphoto library version is supported
            :return: boolean
        """

        # accepted_version =
        if "9.4" not in self._plist["Application Version"]:
            return False
        else:
            return True


    def _validate_iphoto_library(self):
        """validates if iphoto library is validates
           :return: NoneType
           :raises: PyPhotoException
        """

        LOG.debug("validating iPhoto library")

        # Check if path exists
        if not os.path.exists(self._librarypath):
            raise PyPhotoException("Library path does not exist")

        if (os.path.exists(self._make_path("Aperture.aplib"))
            and (not os.path.isfile(self._make_path("ApertureData.xml")))):
            raise PyPhotoException("""Aperture library. Run Aperture first
            to convert it to iPhoto library""")

        # check if AlbumData.xml exists in folder
        if not (os.path.isfile(self._make_path("AlbumData.xml")) or
                os.path.isfile(self._make_path("ApertureData.xml"))):
            raise PyPhotoException("Library path does not exist")


    def _format_path(self, path):
        """returns a reduced path"""
        newpath = path.replace(self._librarypath, "")
        if type(newpath) == unicode:
            newpath = unicodedata.normalize("NFKC", newpath)
        else:
            newpath = unicodedata.normalize("NFKC", unicode(newpath, 'utf-8'))


        if newpath[0] == "/":
            return newpath[1:]
        else:
            return newpath


    def upload_files(self, uploader):
        """upload all files"""
        LOG.debug("uploading files")

        # create uploader and create list of files to be uploaded
        payload = self.join_events_with_masters()

        photos_iphoto = [self._format_path(v.get("OriginalPath",
            v["ImagePath"])) for (_, v) in self.master_images.items()]

        # delete photos that are no longer in the iPhoto library
        if uploader.photos:
            photos_flickr = uploader.photos.keys()
            obsolete_photos = [p for p in photos_flickr
            if p not in photos_iphoto]
            for photoid in obsolete_photos:
                LOG.info("delete photo %s", photoid)
                uploader.delete_photo_by_guid(photoid)

            if len(obsolete_photos) > 0:
                uploader.update_from_server()


        uploader.delete_orphaned_photos()

        # iterate over events
        for name, images in payload.items():
            LOG.info("Uploading Event: %s", name)

            # loop over photos in event
            for guid, path in images.items():
                uploader.upload_photo(self._format_path(path), name, path)





                # # archive images into set
                # if name not in uploader.sets.keys():
                #     LOG.debug("Creating new set: %s", name)

                #     if not photoid:
                #         photoid = uploader.get_photo_by_guid(guid)

                #     setid = uploader.create_set(name, photoid)
                # elif photoid:
                #     setid = uploader.sets[name]["id"]
                #     try:
                #         uploader.add_photo_to_set(setid, photoid)
                #     except Exception, ex:
                #         LOG.debug(ex.message)

                # TODO: reverse compare
