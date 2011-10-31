class EtsyEnvSandbox(object):
    request_token_url = 'http://sandbox.openapi.etsy.com/v2/oauth/request_token'
    access_token_url = 'http://sandbox.openapi.etsy.com/v2/oauth/access_token'
    signin_url = 'https://www.etsy.com/oauth/signin'
    api_url = 'http://sandbox.openapi.etsy.com/v2'

class EtsyEnvProduction(object):
    request_token_url = 'http://openapi.etsy.com/v2/oauth/request_token'
    access_token_url = 'http://openapi.etsy.com/v2/oauth/access_token'
    signin_url = 'https://www.etsy.com/oauth/signin'
    api_url = 'http://openapi.etsy.com/v2'
