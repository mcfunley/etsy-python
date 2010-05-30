from __future__ import with_statement
from contextlib import closing
from simplejson.decoder import JSONDecoder
import urllib2
from urllib import urlencode
from ConfigParser import ConfigParser
import os



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

        d = JSONDecoder()
        self.decode = d.decode

        for method in self._get_method_table():
            self._create_method(**method)


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
        

    def _create_method(self, name, description, uri, **kw):
        def method(**kwargs):
            return self._get(uri, **kwargs)
        method.__name__ = name
        method.__doc__ = description
        setattr(self, name, method)


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

