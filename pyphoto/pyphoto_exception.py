"""
    pyphoto.pyphoto_exception
    ~~~~~~~~~~~~~~~~

    Uploads photos to flickr.

    :copyright: (c) 2013 by Michael Luckeneder.
"""

class PyPhotoException(Exception):
    """docstring for PyPhotoException"""
    def __init__(self, *args, **kwargs):
        super(PyPhotoException, self).__init__(*args, **kwargs)
