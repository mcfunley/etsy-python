from __future__ import with_statement
from contextlib import closing
import simplejson as json
import urllib2
from urllib import urlencode
import os
import re
import tempfile
import time


missing = object()


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




class APIMethod(object):
    def __init__(self, api, spec):
        self.api = api
        self.spec = spec
        self.type_checker = self.api.type_checker
        self.__doc__ = self.spec['description']
        self.compiled = False
    

    def __call__(self, *args, **kwargs):
        if not self.compiled:
            self.compile()
        return self.invoke(*args, **kwargs)


    def compile(self):
        uri = self.spec['uri']
        self.positionals = re.findall('{(.*)}', uri)

        for p in self.positionals:
            uri = uri.replace('{%s}' % p, '%%(%s)s' % p)
        self.uri_format = uri

        self.compiled = True


    def invoke(self, *args, **kwargs):
        if args and not self.positionals:
            raise ValueError(
                'Positional argument(s): %s provided, but this method does '
                'not support them.' % (args,))

        if len(args) > len(self.positionals):
            raise ValueError('Too many positional arguments.')

        for k, v in zip(self.positionals, args):
            if k in kwargs:
                raise ValueError(
                    'Positional argument duplicated in kwargs: %s' % k)
            kwargs[k] = v

        ps = {}
        for p in self.positionals:
            if p not in kwargs:
                raise ValueError("Required argument '%s' not provided." % p)
            ps[p] = kwargs[p]
            del kwargs[p]

        self.type_checker(self.spec, **kwargs)
        return self.api._get(self.uri_format % ps, **kwargs)




class MethodTableCache(object):
    max_age = 60*60*24

    def __init__(self, api, method_cache):
        self.api = api
        self.filename = self.resolve_file(method_cache)


    def etsy_home(self):
        return os.path.expanduser('~/.etsy')


    def resolve_file(self, method_cache):
        if method_cache is missing:
            return self.default_file()
        return method_cache


    def default_file(self):
        etsy_home = self.etsy_home()
        d = etsy_home if os.path.isdir(etsy_home) else tempfile.gettempdir()
        return os.path.join(d, 'methods.json')


    def get(self):
        ms = self.get_cached()
        if not ms:
            ms = self.api._get('/')
            self.cache(ms)
        return ms
        

    def get_cached(self):
        if self.filename is None or not os.path.isfile(self.filename):
            return None
        if time.time() - os.stat(self.filename).st_mtime > self.max_age:
            return None
        with open(self.filename, 'r') as f:
            return json.loads(f.read())


    def cache(self, methods):
        if self.filename is None:
            # not caching
            return
        with open(self.filename, 'w') as f:
            json.dump(methods, f)




class API(object):
    def __init__(self, api_key='', key_file=None, method_cache=missing):
        """
        Creates a new API instance. When called with no arguments, 
        reads the appropriate API key from the default ($HOME/.etsy/keys) 
        file. 

        Parameters:
            api_key      - An explicit API key to use.
            key_file     - A file to read the API keys from. 
            method_cache - A file to save the API method table in for 
                           24 hours. This speeds up the creation of API
                           objects. 

        Only one of api_key and key_file may be passed.

        If method_cache is explicitly set to None, no method table
        caching is performed. If the parameter is not passed, a file in 
        $HOME/.etsy is used if that directory exists. Otherwise, a 
        temp file is used. 
        """
        if not getattr(self, 'api_url', None):
            raise AssertionError('No api_url configured.')

        if self.api_url.endswith('/'):
            raise AssertionError('api_url should not end with a slash.')

        if not getattr(self, 'api_version', None):
            raise AssertionError('API object should define api_version')

        if api_key and key_file:
            raise AssertionError('Keys can be read from a file or passed, '
                                 'but not both.')

        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self._read_key(key_file)

        self.type_checker = TypeChecker()

        self.decode = json.loads

        ms = self._get_method_table(method_cache)
        self._methods = dict([(m['name'], m) for m in ms])

        for method in ms:
            setattr(self, method['name'], APIMethod(self, method))


    def _get_method_table(self, method_cache):
        c = MethodTableCache(self, method_cache)
        return c.get()


    def _read_key(self, key_file):
        key_file = key_file or os.path.expanduser('~/.etsy/keys')
        if not os.path.isfile(key_file):
            raise AssertionError(
                "The key file '%s' does not exist. Create a key file or "
                'pass an API key explicitly.' % key_file)

        gs = {}
        execfile(key_file, gs)
        return gs[self.api_version]
        

    def _get_url(self, url):
        with closing(urllib2.urlopen(url)) as f:
            return f.read() 
  

    def _get(self, url, **kwargs):
        kwargs.update(dict(api_key=self.api_key))
        qs = urlencode(kwargs)
        url = '%s%s?%s' % (self.api_url, url, qs)

        self.last_url = url
        data = self._get_url(url)

        self.data = self.decode(data)
        self.count = self.data['count']
        return self.data['results']

