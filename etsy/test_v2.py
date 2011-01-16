#!/usr/bin/env python

import os, sys
import oauth2 as oauth
import webbrowser
from etsy import Etsy, EtsyEnvSandbox, EtsyEnvProduction
from etsy.oauth import EtsyOAuthClient

logging_enabled = True
etsy_env = EtsyEnvProduction()

def my_log(msg):
    if logging_enabled: print(msg)

def write_config_file(oauth_token):
    os.umask(0077)
    config_file = file('config.py', 'w')

    if config:
        config_file.write("oauth_consumer_key = %r\n" % config.oauth_consumer_key)
        config_file.write("oauth_consumer_secret = %r\n" % config.oauth_consumer_secret)

    if oauth_token:
        config_file.write("oauth_token_key = %r\n" % oauth_token.key)
        config_file.write("oauth_token_secret = %r\n" % oauth_token.secret)

try:
    import config
except ImportError:
    config = None
    write_config_file(oauth_token=None)

if hasattr(config, 'oauth_consumer_key') and hasattr(config, 'oauth_consumer_secret'):
    oauth_client = EtsyOAuthClient(
        oauth_consumer_key=config.oauth_consumer_key,
        oauth_consumer_secret=config.oauth_consumer_secret,
        etsy_env=etsy_env)
else:
    sys.stderr.write('ERROR: You must set oauth_consumer_key and oauth_consumer_secret in config.py\n')
    sys.exit(1)

if hasattr(config, 'oauth_token_key') and hasattr(config, 'oauth_token_secret'):
    oauth_client.token = oauth.Token(
        key=config.oauth_token_key,
        secret=config.oauth_token_secret)
else:
    webbrowser.open(oauth_client.get_signin_url())
    oauth_client.set_oauth_verifier(raw_input('Enter OAuth verifier: '))
    write_config_file(oauth_client.token)

etsy_api = Etsy(etsy_oauth_client=oauth_client, etsy_env=etsy_env, log=my_log)

# print 'oauth access token: (key=%r; secret=%r)' % (oauth_client.token.key, oauth_client.token.secret)

print('findAllShopListingsActive => %r' % etsy_api.findAllShopListingsActive(shop_id=config.user_id, sort_on='created', limit=1))

# print('getListing => %r' % etsy_api.getListing(listing_id=63067548))

print('findAllUserShippingTemplates => %r' % etsy_api.findAllUserShippingTemplates(user_id=config.user_id))

def testCreateListing():
    print "Creating listing..."
    
    result = etsy_api.createListing(
        description=config.description,
        title=config.title,
        price=config.price,
        tags=config.tags,
        materials=config.materials,
        shipping_template_id=config.shipping_template_id,
        shop_section_id=config.shop_section_id,
        quantity=config.quantity)

    listing_id = result[0]['listing_id']

    print "Created listing with listing id %d" % listing_id

    result = etsy_api.uploadListingImage(listing_id=listing_id, image=config.image_file)

    print "Result of uploading image: %r" % result

testCreateListing()

