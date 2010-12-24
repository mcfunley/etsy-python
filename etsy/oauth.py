import oauth2 as oauth
import urllib
from cgi import parse_qsl

class EtsyOAuthClient(oauth.Client):
    request_token_url = 'http://openapi.etsy.com/v2/sandbox/oauth/request_token'
    access_token_url = 'http://openapi.etsy.com/v2/sandbox/oauth/access_token'
    signin_url = 'https://www.etsy.com/oauth/signin'

    def __init__(self, oauth_consumer_key, oauth_consumer_secret):
        consumer = oauth.Consumer(oauth_consumer_key, oauth_consumer_secret)
        super(EtsyOAuthClient, self).__init__(consumer)

    def get_request_token(self, **kwargs):
        request_token_url = '%s?%s' % (self.request_token_url, urllib.urlencode(kwargs))
        resp, content = self.request(request_token_url, 'GET')
        return self._get_token(content)

    def get_signin_url(self, **kwargs):
        self.token = self.get_request_token(**kwargs)

        return self.signin_url + '?' + \
               urllib.urlencode({'oauth_token': self.token.key})

    def get_access_token_url(self, oauth_verifier):
        return self.access_token_url + '?' + \
               urllib.urlencode({'oauth_verifier': oauth_verifier})

    def get_access_token(self, oauth_verifier):
        resp, content = self.request(self.get_access_token_url(oauth_verifier), 'GET')
        return self._get_token(content)

    def set_oauth_verifier(self, oauth_verifier):
        self.token = self.get_access_token(oauth_verifier)

    def do_oauth_request(self, url, http_method, content_type, body):
        if content_type and content_type != 'application/x-www-form-urlencoded':
            resp, content = self.request(url, http_method, body=body, headers={'Content-Type': content_type})
        else:
            resp, content = self.request(url, http_method, body=body)

        return content

    def _get_token(self, content):
        d = dict(parse_qsl(content))

        return oauth.Token(d['oauth_token'], d['oauth_token_secret'])


