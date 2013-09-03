"""
    pyphoto.flickr_uploader
    ~~~~~~~~~~~~~~~~

    Uploads photos to flickr.

    :copyright: (c) 2013 by Michael Luckeneder.
"""
from __future__ import absolute_import
import flickrapi
import logging
from urllib2 import HTTPError
from flickrapi.exceptions import FlickrError
from .retrier import retrier
from functools import partial

LOG = logging.getLogger()


class FlickrUploader(object):
    """represents a flickr instance"""
    def __init__(self, **kwargs):

        self.sets = None
        self.photos = []

        self.flickr_key = kwargs.pop('flickr_key')
        self.flickr_secret = kwargs.pop('flickr_secret')
        self.flickr_namespace = kwargs.get('flickr_namespace', "pyphoto")
        self.pyphoto_setid = None

        # get auth token and update sets, photos
        self.flickr = self._authorize_flickr()
        self.update_from_server()

    def update_from_server(self):
        """update set sand photos from flickr"""
        self.sets = self.get_sets()
        self.photos = self.get_photos()

    @retrier
    def get_sets(self):
        """get a dict of sets
           :return: dict()
        """
        # get response
        sets_response = self.flickr.photosets_getList()
        set_list = list(sets_response)[0]

        sets = {}
        # generate set list
        for photo_set in set_list.iter('photoset'):
            title = photo_set.find('title').text
            description = photo_set.find('description').text
            set_info = {'id': photo_set.attrib['id'],
                        'date_update': photo_set.attrib['date_update'],
                        'description': description}

            sets[title] = set_info
        return sets

    @retrier
    def upload_file(self, filename, guid):
        """uploads an image with filename and guid"""
        res = self.flickr.upload(filename=filename,
                                 title=guid,
                                 description=guid,
                                 is_public=0,
                                 is_family=0,
                                 is_friend=0)

        # return the flickr id of the photo
        return res.find('photoid').text

    def get_photos(self, items_per_page=500):
        """get a list of photos
           :return: dict()
        """

        # TODO compress
        if self.flickr_namespace not in self.sets:
            return []

        # monkey patch for flickrapi problem
        pages = partial(self.flickr.photosets_getPhotos,
            photoset_id=self.sets[self.flickr_namespace]["id"],
            per_page=items_per_page)

        pages = retrier(pages)
        num_pages = page = 1

        photos = {}
        while page <= num_pages:
            LOG.debug("Retrieving page %i of set %s",
                      page, self.flickr_namespace)
            res = pages(page=page)
            num_pages = int(res.find('photoset').get('pages'))
            page += 1


            for photo in list(res)[0].iter('photo'):
                photos[photo.attrib['title']] = photo.attrib
            # photo_list.append(list(res.find('photo')))

            # for photo in res.find('photos'):
            #     if photo.get('title') == guid:
            #         return photo.get('id')

        # return None
        # photo_list = list(photos)[0]

        # photos = {}
        # for photo in photo_list:
        #     photos[photo.attrib['title']] = photo.attrib
        return photos

    def get_photos_for_set(self, photoset_id):
        """get a list of photos
           :return: dict()
        """

        # monkey patch for flickrapi problem
        pages = partial(self.flickr.photosets_getPhotos,
            photoset_id=photoset_id,
            per_page=500)

        pages = retrier(pages)
        num_pages = page = 1

        photos = {}
        while page <= num_pages:
            LOG.debug("Retrieving page %i of set %s",
                      page, photoset_id)
            res = pages(page=page)
            num_pages = int(res.find('photoset').get('pages'))
            page += 1


            for photo in list(res)[0].iter('photo'):
                photos[photo.attrib['title']] = photo.attrib
            # photo_list.append(list(res.find('photo')))

            # for photo in res.find('photos'):
            #     if photo.get('title') == guid:
            #         return photo.get('id')

        # return None
        # photo_list = list(photos)[0]

        # photos = {}
        # for photo in photo_list:
        #     photos[photo.attrib['title']] = photo.attrib
        return photos

    @retrier
    def create_set(self, title, photo_id):
        """docstring"""
        if not (title and photo_id):
            return False
        res = self.flickr.photosets_create(title=title,
                                           primary_photo_id=photo_id)
        self.update_from_server()
        return res.find('photoset').attrib['id']

    @retrier
    def add_photo_to_set(self, setid, photoid):
        """docstring"""
        self.flickr.photosets_addPhoto(photoset_id=setid,
                                             photo_id=photoid)

        return True

    def get_photo_by_guid(self, guid):
        """docstring"""
        if not guid in self.photos:
            return None
        return self.photos[guid]["id"]
        # monkey patch for flickrapi problem
        # pages = partial(self.flickr.photos_search, user_id="me", per_page=500)
        # num_pages = page = 1

        # while page <= num_pages:
        #     LOG.debug("Retrieving page %i" % (page))
        #     res = pages(page=page)
        #     num_pages = int(res.find('photos').get('pages'))
        #     page += 1

        #     for photo in res.find('photos'):
        #         if photo.get('title') == guid:
        #             return photo.get('id')

        # return None

    def delete_orphaned_photos(self):
        """delete photos that were uploaded but don't exist
           in any set
        """
        LOG.info("deleting orphaned photos")
        set_photos = []
        for k, v in self.sets.items():
            if k == self.flickr_namespace:
                continue
            set_photos.extend(self.get_photos_for_set(v["id"]))

        orphaned_photos = [p for p in self.photos if p not in set_photos]
        for photoid in orphaned_photos:
            LOG.info("delete photo %s", photoid)
            self.delete_photo_by_guid(photoid)

        if len(orphaned_photos) > 0:
            self.update_from_server()


    def delete_photo_by_guid(self, guid):
        """deletes a photo by GUID string"""
        photo_id = self.get_photo_by_guid(guid)
        if not photo_id:
            return None
        retval =  self.flickr.photos_delete(photo_id=photo_id)

        return retval

    def _authorize_flickr(self, perms="delete"):
        """taken from flickrapi source, generates auth token and authorizes
           everything
        """
        flickr = flickrapi.FlickrAPI(self.flickr_key, self.flickr_secret)
        (token, frob) = flickr.get_token_part_one(perms=perms)
        if not token:
            raw_input("Press ENTER after you authorized this program")
        token = flickr.get_token_part_two((token, frob))

        return flickrapi.FlickrAPI(self.flickr_key, self.flickr_secret,
                                   token=token)

    # def _initialize_main_set(self):


    def upload_photo(self, guid, setname, photopath):
        """upload a photo and handle set issues"""

        photoid = None
        photo_exists = False
        if guid not in self.photos:
            LOG.info("  Uploading Image: %s",
                guid)
            photoid = self.upload_file(photopath, guid)

        else:
            LOG.info("  Image exists: %s", guid)
            photo_exists = True
            photoid = self.get_photo_by_guid(guid)


        # if pyphoto set doesn't exist yet
        if self.flickr_namespace not in self.sets.keys():
            self.pyphoto_setid = self.create_set(
                self.flickr_namespace, photoid)
        elif not photo_exists:
            if not self.pyphoto_setid:
                self.pyphoto_setid = self.sets[self.flickr_namespace]["id"]
            self.add_photo_to_set(self.pyphoto_setid, photoid)


        if setname not in self.sets.keys():
            LOG.debug("Creating new set: %s", setname)

            setid = self.create_set(setname, photoid)
        elif not photo_exists:
            setid = self.sets[setname]["id"]
            self.add_photo_to_set(setid, photoid)


