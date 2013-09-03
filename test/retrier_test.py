"""retrier lib testcases"""
from __future__ import absolute_import
from testify import *
from pyphoto import (retrier, PyPhotoException)
from urllib2 import HTTPError

class RetrierTest(TestCase):
    """iphoto library testcase"""

    @setup
    def setup_the_test(self):
        self.counter = 0

    @retrier
    def a_method(self):
        """a test method"""
        if self.counter < 4:
            self.counter += 1
            raise PyPhotoException
        else:
            return True

    def test_functioning_of_retrier(self):
        retval = self.a_method()

        assert(retval)
        assert_equals(self.counter, 4)




if __name__ == "__main__":
    run()
