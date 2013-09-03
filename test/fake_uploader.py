"""Fake Uploader"""
from testify import *

class FakeUploader(object):
    """fake uploader"""
    def __init__(self, **kwargs):

        self.sets = None
        self.photos = []

        self.mock_sets = set()
        self.mock_photos = set()
        self.mock_deleted_photos = set()

    def get_sets(self):
        pass

    def upload_file(self, filename, guid):
        pass

    def get_photos(self):
        pass


    def get_photos_for_set(self, photoset_id):
        """docstring"""
        pass

    def create_set(self, title, photo_id):
        """docstring"""
        pass

    def add_photo_to_set(self, setid, photoid):
        """docstring"""
        pass

    def get_photo_by_guid(self, guid):
        """docstring"""
        pass

    def delete_photo_by_guid(self, guid):
        """deletes a photo by GUID string"""
        self.mock_deleted_photos.add(guid)

    def _authorize_flickr(self, perms="delete"):
        """taken from flickrapi source, generates auth token and authorizes
           everything
        """
        pass

    def delete_orphaned_photos(self):
        pass
    def update_from_server(self):
        pass
    def upload_photo(self, guid, setname, photopath):
        """upload a photo and handle set issues"""
        self.mock_sets.add(setname)
        self.mock_photos.add(guid)


