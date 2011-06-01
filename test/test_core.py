from __future__ import with_statement
from etsy._core import API, MethodTableCache, missing
from cgi import parse_qs
from urlparse import urlparse
import os
from util import Test
import tempfile

    

class MockAPI(API):
    api_url = 'http://host'
    api_version = 'v1'


    def etsy_home(self):
        return Test.scratch_dir


    def get_method_table(self, *args):
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


    def _get_url(self, url, http_method, content_type, body):
        return '{ "count": 1, "results": [3] }'



class MockLog(object):
    def __init__(self, test):
        self.lines = []
        self.test = test

    def __call__(self, msg):
        self.lines.append(msg)


    def assertLine(self, msg):
        failmsg = 'Could not find "%s" in the log. The log was:\n\n%s' % (
            msg, '\n'.join(['   %s' % x for x in self.lines]))
        self.test.assertTrue(msg in self.lines, failmsg)



class CoreTests(Test):
    def setUp(self):
        self.api = MockAPI('apikey', log=MockLog(self))


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


    def test_parameter_type_long(self):
        self.api.testMethod(test_id=1L, limit=5L)
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


    def test_api_key_and_key_file_both_passed(self):
        msg = self.assertRaises(AssertionError, MockAPI, 
                                api_key='x', key_file='y')
        self.assertEqual('Keys can be read from a file or passed, but not both.',
                         msg)


    def test_logging_works(self):
        self.api.log('foo')
        self.api.log.assertLine('foo')


    def test_log_at_startup(self):
        self.api.log.assertLine('Creating v1 Etsy API, base url=http://host.')






class MockAPI_NoMethods(MockAPI):
    def _get_methods(self, method_cache):
        pass



class MethodTableCacheTests(Test):


    def cache(self, method_cache=missing):
        self.api = MockAPI_NoMethods('apikey')
        self._cache = MethodTableCache(self.api, method_cache)
        return self._cache


    def test_uses_etsy_home_if_exists(self):
        c = self.cache()
        self.assertEqual(os.path.dirname(c.filename), self.scratch_dir)


    def test_uses_temp_dir_if_no_etsy_home(self):
        self.delete_scratch()
        c = self.cache()
        self.assertEqual(os.path.dirname(c.filename), tempfile.gettempdir())


    def test_uses_provided_file(self):
        fn = os.path.join(self.scratch_dir, 'foo.json')
        self.assertEqual(self.cache(method_cache=fn).filename, fn)


    def test_multiple_versions(self):
        c = self.cache()

        class MockAPI2(MockAPI):
            api_version = 'v3'

        self.assertNotEqual(MockAPI2('key').method_cache.filename, c.filename)


    def get_uncached(self):
        c = self.cache()
        return c.get()
    

    def test_no_cache_file_returns_results(self):
        self.assertEqual(2, len(self.get_uncached()))


    def test_no_cache_file_writes_cache(self):
        self.get_uncached()
        self.assertTrue(self._cache.wrote_cache)

    
    def test_no_cache_file(self):
        self.get_uncached()
        self.assertFalse(self._cache.used_cache)


    def get_cached(self):
        c = self.cache()
        c.get()
        c = self.cache()
        return c.get()


    def test_caching(self):
        self.get_cached()
        self.assertTrue(self._cache.used_cache)


    def test_caching_returns_results(self):
        self.assertEqual(2, len(self.get_cached()))


    def test_caching_doesnt_overwrite_cache(self):
        self.get_cached()
        self.assertFalse(self._cache.wrote_cache)


    def make_old_cache(self):
        self.get_cached()
        fn = self._cache.filename
        s = os.stat(fn)
        os.utime(fn, (s.st_atime, s.st_mtime - 48*60*60))


    def test_expired(self):
        self.make_old_cache()
        c = self.cache()
        c.get()
        self.assertFalse(c.used_cache)
        
    
    def test_none_passed_does_not_cache(self):
        self.get_cached()
        c = self.cache(method_cache=None)
        c.get()
        self.assertFalse(c.used_cache)


    def log_tester(self, method_cache=missing):
        return MockAPI('key', method_cache=method_cache, log=MockLog(self))


    def test_logs_when_not_using_cache(self):
        api = self.log_tester(None)
        api.log.assertLine('Not using cached method table.')


    def test_logs_when_method_table_too_old(self):
        self.make_old_cache()
        self.log_tester().log.assertLine('Method table too old.')

    
    def test_logs_when_reading_cache(self):
        api = MockAPI('key')
        self.log_tester().log.assertLine('Reading method table cache: %s' % 
                                         api.method_cache.filename)


    def test_logs_when_not_writing_new_cache(self):
        api = self.log_tester(None)
        api.log.assertLine(
            'Method table caching disabled, not writing new cache.')


    def test_logs_when_writing_new_cache(self):
        t = self.log_tester()
        t.log.assertLine('Wrote method table cache: %s' % 
                         t.method_cache.filename)

