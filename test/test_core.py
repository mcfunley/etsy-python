from __future__ import with_statement
from etsy._core import API
from cgi import parse_qs
from urlparse import urlparse
import os
from util import Test
    

class MockAPI(API):
    api_url = 'http://host'
    api_version = 'v1'

    def _get_method_table(self):
        return [{'name': 'testMethod', 
                 'uri': '/test/{test_id}', 
                 'http_method': 'GET', 
                 'params': { 
                     'limit': 'int',
                     'test_id': 'user_id_or_name',
                     'offset': 'int',
                     'fizz': 'enum(foo, bar, baz)',
                     'buzz': 'float',
                     'blah': 'unknown type',
                     'kind': 'string',
                     },
                 'type': 'int', 
                 'description': 'test method.'},
                {'name': 'noPositionals',
                 'uri': '/blah',
                 'http_method': 'GET',
                 'params': {'foo': 'int'},
                 'type': 'int',
                 'description': 'no pos arguments'}]


    def _get_url(self, url):
        return '{ "count": 1, "results": [3] }'



class CoreTests(Test):
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
        msg = self.assertRaises(AssertionError, API, '')
        self.assertEqual('No api_url configured.', msg)


    def test_api_url_cannot_end_with_slash(self):
        class Foo(API):
            api_url = 'http://host/'

        msg = self.assertRaises(AssertionError, Foo, '')
        self.assertEqual('api_url should not end with a slash.', msg)


    def test_api_should_define_version(self):
        class Foo(API):
            api_url = 'http://host'

        msg = self.assertRaises(AssertionError, Foo)
        self.assertEqual(msg, 'API object should define api_version')


    def test_key_file_does_not_exist(self):
        msg = self.assertRaises(AssertionError, MockAPI, 
                                key_file='this does not exist')
        self.assertTrue("'this does not exist' does not exist" in msg)


    def test_reading_api_key(self):
        with open('testkeys', 'w') as f:
            f.write("v1 = 'abcdef'")
        try:
            self.assertEqual(MockAPI(key_file='testkeys').api_key, 'abcdef')
        finally:
            os.unlink('testkeys')


    def test_unrecognized_kwarg(self):
        msg = self.assertRaises(ValueError, self.api.testMethod, 
                                test_id=1, not_an_arg=1)
        self.assertEqual(msg, 'Unexpected argument: not_an_arg=1')

    
    def test_unknown_parameter_type_is_passed(self):
        self.api.testMethod(test_id=1, blah=1)
        self.assertEqual(self.last_query()['blah'], ['1'])


    def test_parameter_type_int(self):
        self.api.testMethod(test_id=1, limit=5)
        self.assertEqual(self.last_query()['limit'], ['5'])


    def bad_value_msg(self, name, t, v):
        return "Bad value for parameter %s of type '%s' - %s" % (name, t, v)

    def test_invalid_parameter_type_int(self):
        msg = self.assertRaises(ValueError, self.api.testMethod, 
                                test_id=1, limit=5.6)
        self.assertEqual(msg, self.bad_value_msg('limit', 'int', 5.6))


    def test_parameter_type_float(self):
        self.api.testMethod(test_id=1, buzz=42.1)
        self.assertEqual(self.last_query()['buzz'], ['42.1'])


    def test_invalid_parameter_type_float(self):
        msg = self.assertRaises(ValueError, self.api.testMethod, 
                                test_id=1, buzz='x')
        self.assertEqual(msg, self.bad_value_msg('buzz', 'float', 'x'))

    
    def test_int_accepted_as_float(self):
        self.api.testMethod(test_id=1, buzz=3)
        self.assertEqual(self.last_query()['buzz'], ['3'])

        
    def test_parameter_type_enum(self):
        self.api.testMethod(test_id=1, fizz='bar')
        self.assertEqual(self.last_query()['fizz'], ['bar'])


    def test_invalid_parameter_type_enum(self):
        msg = self.assertRaises(ValueError, self.api.testMethod, 
                                test_id=1, fizz='goo')
        self.assertEqual(msg, self.bad_value_msg(
                'fizz', 'enum(foo, bar, baz)', 'goo'))


    def test_parameter_type_string(self):
        self.api.testMethod(test_id=1, kind='blah')
        self.assertEqual(self.last_query()['kind'], ['blah'])


    def test_invalid_parameter_type_string(self):
        msg = self.assertRaises(ValueError, self.api.testMethod, 
                                test_id=1, kind=Test)
        self.assertEqual(msg, self.bad_value_msg('kind', 'string', Test))


    def test_url_arguments_work_positionally(self):
        self.api.testMethod('foo')
        self.assertEqual(self.api.last_url, 
                         'http://host/test/foo?api_key=apikey')


    def test_method_with_no_positionals_doesnt_accept_them(self):
        msg = self.assertRaises(ValueError, self.api.noPositionals, 1, 2)
        self.assertEqual('Positional argument(s): (1, 2) provided, but this '
                         'method does not support them.', msg)

    
    def test_too_many_positionals(self):
        msg = self.assertRaises(ValueError, self.api.testMethod, 1, 2)
        self.assertEqual('Too many positional arguments.', msg)


    def test_positional_argument_not_provided(self):
        msg = self.assertRaises(ValueError, self.api.testMethod)
        self.assertEqual("Required argument 'test_id' not provided.", msg)


    def test_positional_argument_duplicated_in_kwargs(self):
        msg = self.assertRaises(ValueError, self.api.testMethod, 1, test_id=2)
        self.assertEqual('Positional argument duplicated in kwargs: test_id', 
                         msg)
