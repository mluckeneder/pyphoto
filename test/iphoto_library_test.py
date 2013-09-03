"""iPhoto Library testcases"""
from __future__ import absolute_import
from testify import *
from pyphoto import (IPhotoLibrary, PyPhotoException)
from . import expected
from .fake_uploader import FakeUploader

LIBRARY_PATH = "./test/mock/iPhotoTestLibrary.photolibrary"
BROKEN_LIBRARY_PATH = "./test/mock/BrokeniPhotoTestLibrary.photolibrary"
OLD_VERSION_LIBRARY_PATH = "./test/mock/OldVersion.photolibrary"

class IPhotoLibraryTest(TestCase):
    """iphoto library testcase"""
    @setup
    def init_the_class(self):
        self.photo_lib = IPhotoLibrary(LIBRARY_PATH)

    def test_correct_instantiation(self):
        assert_isinstance(self.photo_lib, IPhotoLibrary)

    def test_incorrect_path1(self):
        with assert_raises(PyPhotoException):
            IPhotoLibrary("/tmp/foo/bar")

        with assert_raises(PyPhotoException):
            IPhotoLibrary("./")

    def test_version(self):
        """tests an invalid version"""
        with assert_raises(PyPhotoException):
            IPhotoLibrary(OLD_VERSION_LIBRARY_PATH)

    def testtemp_aperture(self):
        pass


    def test_correct_plist_parsing(self):
        assert_equal(len(self.photo_lib._plist), 9)
        assert_equal(len(self.photo_lib.events), 2)
        assert_equal(len(self.photo_lib.master_images), 30)

    def test_broken_plist_file(self):
        with assert_raises(Exception):
            IPhotoLibrary(BROKEN_LIBRARY_PATH)

    def test_retrieve_list_of_master_files(self):
        master_files = self.photo_lib.get_list_of_master_files()
        assert_equals(expected.MASTER_FILES, master_files)

    def test_join_events_with_masters(self):
        events_masters = self.photo_lib.join_events_with_masters()
        assert_equals(expected.JOINED_EVENTS_MASTER_FILES, events_masters)


    def test_format_path(self):
        fake_path = "%s/Master" % LIBRARY_PATH
        assert_equals("Master", self.photo_lib._format_path(fake_path))
        assert_equals("Master", self.photo_lib._format_path("Master"))

    def test_upload_files(self):
        uploader = FakeUploader()

        self.photo_lib.upload_files(uploader)

        assert_equals(len(uploader.mock_sets), 2)
        assert_equals(len(uploader.mock_photos), 30)
        exp_guids = set([self.photo_lib._format_path(v)
            for v in expected.MASTER_FILES.values()])

        assert_equals(len(exp_guids - uploader.mock_photos), 0)

        uploader = FakeUploader()
        uploader.photos = {v: []
        for v in ["f","o","oo"]}


        self.photo_lib.upload_files(uploader)

        assert_equals(len(uploader.mock_deleted_photos), 3)
        assert_equals(len(uploader.mock_photos), 30)



if __name__ == "__main__":
    run()
