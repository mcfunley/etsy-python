import oauth2 as oauth
import urllib
from cgi import parse_qsl
from etsy_env import EtsyEnvSandbox, EtsyEnvProduction

EtsyOAuthToken = oauth.Token

class EtsyOAuthClient(oauth.Client):
    def __init__(self, oauth_consumer_key, oauth_consumer_secret, etsy_env=EtsyEnvSandbox(), token=None, logger=None):
        consumer = oauth.Consumer(oauth_consumer_key, oauth_consumer_secret)
        super(EtsyOAuthClient, self).__init__(consumer)
        self.request_token_url = etsy_env.request_token_url
        self.access_token_url = etsy_env.access_token_url
        self.signin_url = etsy_env.signin_url
        self.token = token
        self.logger = logger

    def get_request_token(self, **kwargs):
        request_token_url = '%s?%s' % (self.request_token_url, urllib.urlencode(kwargs))
        resp, content = self.request(request_token_url, 'GET')
        return self._get_token(content)

    def get_signin_url(self, **kwargs):
        self.token = self.get_request_token(**kwargs)

        if self.token is None: return None

        return self.signin_url + '?' + \
               urllib.urlencode({'oauth_token': self.token.key})

    def get_access_token(self, oauth_verifier):
        self.token.set_verifier(oauth_verifier)
        resp, content = self.request(self.access_token_url, 'GET')
        return self._get_token(content)

    def set_oauth_verifier(self, oauth_verifier):
        self.token = self.get_access_token(oauth_verifier)

    def do_oauth_request(self, url, http_method, content_type, body):
        if content_type and content_type != 'application/x-www-form-urlencoded':
            resp, content = self.request(url, http_method, body=body, headers={'Content-Type': content_type})
        else:
            resp, content = self.request(url, http_method, body=body)

        if self.logger:
            self.logger.debug('do_oauth_request: content = %r' % content)

        return content

    def _get_token(self, content):
        d = dict(parse_qsl(content))

        try:
            return oauth.Token(d['oauth_token'], d['oauth_token_secret'])
        except KeyError, e:
            return None
