from __future__ import with_statement
from unittest import TestCase
from etsy._core import API
from cgi import parse_qs
from urlparse import urlparse
import os

    

class MockAPI(API):
    api_url = 'http://host'
    api_version = 'v1'

    def _get_method_table(self):
        return [{'name': 'testMethod', 
                 'uri': '/test/{test_id}', 
                 'http_method': 'GET', 
                 'params': { 
                     'limit': 'int',
                     'test_id': 'int',
                     'offset': 'int',
                     },
                 'type': 'int', 
                 'description': 'test method.'}]


    def _get_url(self, url):
        return '{ "count": 1, "results": [3] }'



class CoreTests(TestCase):
    def setUp(self):
        self.api = MockAPI('apikey')


    def last_query(self):
        qs = urlparse(self.api.last_url).query
        return parse_qs(qs)


    def test_method_created(self):
        self.assertTrue('testMethod' in dir(self.api))


    def test_url_params(self):
        self.api.testMethod(test_id='foo')
        self.assertEqual(self.api.last_url, 
                         'http://host/test/foo?api_key=apikey')


    def test_count_saved(self):
        self.api.testMethod(test_id='foo')
        self.assertTrue(self.api.count)


    def test_results_returned(self):
        x = self.api.testMethod(test_id='foo')
        self.assertEquals(x, [3])


    def test_query_params(self):
        self.api.testMethod(test_id='foo', limit=1)
        self.assertEqual(self.last_query(), {
                'api_key': ['apikey'],
                'limit': ['1'],
                })


    def test_docstring_set(self):
        self.assertEquals(self.api.testMethod.__doc__,
                          'test method.')

    
    def test_api_url_required(self):
        try:
            API('')
        except AssertionError, e:
            self.assertEqual('No api_url configured.', e.message)
        else:
            self.fail('should have failed')


    def test_api_url_cannot_end_with_slash(self):
        class Foo(API):
            api_url = 'http://host/'

        try:
            Foo('')
        except AssertionError, e:
            self.assertEqual('api_url should not end with a slash.', 
                             e.message)
        else:
            self.fail('should have failed')


    def test_api_should_define_version(self):
        class Foo(API):
            api_url = 'http://host'

        try:
            Foo()
        except AssertionError, e:
            self.assertEqual(e.message, 'API object should define api_version')
        else:
            self.fail('should have failed')


    def test_key_file_does_not_exist(self):
        try:
            MockAPI(key_file='this does not exist')
        except AssertionError, e:
            self.assertTrue("'this does not exist' does not exist" 
                            in e.message)
        else:
            self.fail('should have failed')


    def test_reading_api_key(self):
        with open('testkeys', 'w') as f:
            f.write("v1 = 'abcdef'")
        try:
            self.assertEqual(MockAPI(key_file='testkeys').api_key, 'abcdef')
        finally:
            os.unlink('testkeys')


            


