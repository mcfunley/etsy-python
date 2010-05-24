from __future__ import with_statement
from contextlib import closing
from simplejson.decoder import JSONDecoder
import urllib2
from urllib import urlencode



class Etsy(object):
    api_url = 'http://beta-api.etsy.com/v1'
    
    def __init__(self, api_key):
        self.api_key = api_key

        d = JSONDecoder()
        self.decode = d.decode

        for method in self.get('/'):
            self.create_method(**method)
        

    def create_method(self, name, description, uri, **kw):
        def method(**kwargs):
            return self.get(uri, **kwargs)
        method.__name__ = name
        method.__doc__ = description
        setattr(self, name, method)


    def get(self, url, **kwargs):
        for k, v in kwargs.items():
            arg = '{%s}' % k
            if arg in url:
                url = url.replace(arg, v)

        kwargs.update(dict(api_key=self.api_key))
        qs = urlencode(kwargs)
        url = '%s%s?%s' % (self.api_url, url, qs)
        with closing(urllib2.urlopen(url)) as f:
            data = f.read()

        self.data = self.decode(data)
        self.count = self.data['count']
        return self.data['results']



