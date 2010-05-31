from __future__ import with_statement
from unittest import TestCase
from etsy import EtsyV1 as Etsy


class V1Tests(TestCase):
    def test_v1_api_works(self):
        api = Etsy()
        x = api.getUserDetails(user_id='mcfunley')
        self.assertEqual(x[0]['user_name'], 'mcfunley')

