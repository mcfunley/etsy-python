class EtsyEnvSandbox(object):
    request_token_url = 'http://openapi.etsy.com/v2/sandbox/oauth/request_token'
    access_token_url = 'http://openapi.etsy.com/v2/sandbox/oauth/access_token'
    signin_url = 'https://www.etsy.com/oauth/signin'
    public_api_url = 'http://openapi.etsy.com/v2/sandbox/public'
    private_api_url = 'http://openapi.etsy.com/v2/sandbox/private'

class EtsyEnvProduction(object):
    request_token_url = 'http://openapi.etsy.com/v2/oauth/request_token'
    access_token_url = 'http://openapi.etsy.com/v2/oauth/access_token'
    signin_url = 'https://www.etsy.com/oauth/signin'
    public_api_url = 'http://openapi.etsy.com/v2/public'
    private_api_url = 'http://openapi.etsy.com/v2/private'


