"""flickr uploader testcases"""
from __future__ import absolute_import
from testify import *
from pyphoto import FlickrUploader
from . import expected
from . import config

class FlickrUploaderTest(TestCase):
    """flickr uploader test"""

    def create_uploader(self):
        self.uploader =  FlickrUploader(flickr_key=config.API_KEY,
                                       flickr_secret=config.API_SECRET,
                                       flickr_namespace="testify_test")

        return self.uploader


    @setup
    def init_the_class(self):
        """initialize the test"""
        self.uploader = None

    def test_correct_instantiation(self):
        uploader = self.create_uploader()
        assert_isinstance(uploader, FlickrUploader)



    def test_upload_file(self):
        """tests the upload capabilities"""
        uploader = self.create_uploader()
        uploader.upload_photo("pyphoto_testify_test1",
            "testify_testset",
            "./test/mock/out0.jpg")
        uploader.update_from_server()

        assert_equals(len(uploader.photos), 1)
        assert_in("testify_testset", uploader.sets)

    def test_upload_file_image_exists(self):
        """tests with existing image"""
        uploader = self.create_uploader()
        uploader.upload_photo("pyphoto_testify_test1",
            "testify_testset",
            "./test/mock/out0.jpg")
        uploader.upload_photo("pyphoto_testify_test1",
            "testify_testset",
            "./test/mock/out0.jpg")
        uploader.update_from_server()

        assert_equals(len(uploader.photos), 1)
        assert_in("testify_testset", uploader.sets)

    def test_multiple_upload_files(self):
        """further tests upload"""
        uploader = self.create_uploader()
        uploader.upload_photo("pyphoto_testify_test1", "testify_testset",
            "./test/mock/out0.jpg")
        uploader.upload_photo("pyphoto_testify_test2", "testify_testset",
            "./test/mock/out1.jpg")
        uploader.upload_photo("pyphoto_testify_test3", "testify_testset2",
            "./test/mock/out2.jpg")
        uploader.update_from_server()

        assert_equals(len(uploader.photos), 3)
        exp_set = len(set(["pyphoto_testify_test1", "pyphoto_testify_test2",
            "pyphoto_testify_test3"]) - set(uploader.photos.keys()))
        assert_equals(exp_set, 0)

    def test_delete_orphaned_photos(self):
        """tests the correct removal of orphaned files"""
        uploader = self.create_uploader()
        uploader.upload_photo("pyphoto_testify_test1", "",
            "./test/mock/out0.jpg")
        uploader.upload_photo("pyphoto_testify_test2", "testify_testset",
            "./test/mock/out1.jpg")
        uploader.upload_photo("pyphoto_testify_test3", "testify_testset2",
            "./test/mock/out2.jpg")
        assert_equals(len(uploader.photos), 3)

        uploader.delete_orphaned_photos()
        uploader.update_from_server()

        assert_equals(len(uploader.photos), 2)




    def test_wrong_parameters(self):
        with assert_raises(Exception):
            FlickrUploader()
        with assert_raises(Exception):
            FlickrUploader(flickr_key="foo")
        with assert_raises(Exception):
            FlickrUploader(flickr_secret="foobar")


    @teardown
    def teardown_the_class(self):
        """teardown action"""
        if self.uploader:
            self.uploader.delete_photo_by_guid("pyphoto_testify_test1")
            self.uploader.delete_photo_by_guid("pyphoto_testify_test2")
            self.uploader.delete_photo_by_guid("pyphoto_testify_test3")







if __name__ == "__main__":
    run()
