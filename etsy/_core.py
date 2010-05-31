from __future__ import with_statement
from contextlib import closing
from simplejson.decoder import JSONDecoder
import urllib2
from urllib import urlencode
from ConfigParser import ConfigParser
import os



class TypeChecker(object):
    def __init__(self):
        self.checkers = {
            'int': self.check_int,
            'float': self.check_float,
            'string': self.check_string,
            }


    def __call__(self, method, **kwargs):
        params = method['params']
        for k, v in kwargs.items():
            if k not in params:
                raise ValueError('Unexpected argument: %s=%s' % (k, v))
            
            t = params[k]
            checker = self.checkers.get(t, None) or self.compile(t)
            ok, converted = checker(v)
            if not ok:
                raise ValueError(
                    "Bad value for parameter %s of type '%s' - %s" % (k, t, v))
            kwargs[k] = converted


    def compile(self, t):
        if t.startswith('enum'):
            f = self.compile_enum(t)
        else:
            f = self.always_ok
        self.checkers[t] = f
        return f


    def compile_enum(self, t):
        terms = [x.strip() for x in t[5:-1].split(',')]
        def check_enum(value):
            return (value in terms), value
        return check_enum


    def always_ok(self, value):
        return True, value


    def check_int(self, value):
        return isinstance(value, int), value

    
    def check_float(self, value):
        if isinstance(value, int):
            return True, value
        return isinstance(value, float), value

    
    def check_string(self, value):
        return isinstance(value, basestring), value

    



class API(object):
    def __init__(self, api_key='', key_file=None):
        if not getattr(self, 'api_url', None):
            raise AssertionError('No api_url configured.')

        if self.api_url.endswith('/'):
            raise AssertionError('api_url should not end with a slash.')

        if not getattr(self, 'api_version', None):
            raise AssertionError('API object should define api_version')

        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self._read_key(key_file)

        self.type_checker = TypeChecker()

        d = JSONDecoder()
        self.decode = d.decode

        ms = self._get_method_table()
        self._methods = dict([(m['name'], m) for m in ms])

        for method in ms:
            self._create_method(method)


    def _get_method_table(self):
        return self._get('/')


    def _read_key(self, key_file):
        key_file = key_file or os.path.expanduser('~/.etsy/keys')
        if not os.path.isfile(key_file):
            raise AssertionError(
                "The key file '%s' does not exist. Create a key file or "
                'pass an API key explicitly.' % key_file)

        gs = {}
        execfile(key_file, gs)
        return gs[self.api_version]
        

    def _create_method(self, m):
        def method(**kwargs):
            return self._invoke(m, **kwargs)
        method.__name__ = m['name']
        method.__doc__ = m['description']
        setattr(self, m['name'], method)


    def _invoke(self, m, **kwargs):
        self.type_checker(m, **kwargs)
        return self._get(m['uri'], **kwargs)


    def _get_url(self, url):
        with closing(urllib2.urlopen(url)) as f:
            return f.read() 
  

    def _get(self, url, **kwargs):
        for k, v in kwargs.items():
            arg = '{%s}' % k
            if arg in url:
                url = url.replace(arg, v)
                del kwargs[k]

        kwargs.update(dict(api_key=self.api_key))
        qs = urlencode(kwargs)
        url = '%s%s?%s' % (self.api_url, url, qs)

        self.last_url = url
        data = self._get_url(url)

        self.data = self.decode(data)
        self.count = self.data['count']
        return self.data['results']

