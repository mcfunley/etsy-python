# etsy-python
Python access to the Etsy API

By Dan McKinley - dan@etsy.com - [http://mcfunley.com](http://mcfunley.com)

## Installation

The simplest way to install the module is using 
[setuptools](http://pypi.python.org/pypi/setuptools).

<pre>
$ easy_install etsy
</pre>

To install from source, extract the tarball and use the following commands.

<pre>
$ python setup.py build
$ sudo python setup.py install
</pre>

## Simple Example

To use, first [register for an Etsy developer key](http://developer.etsy.com/).
Below is an example session. 

<pre>
$ python
python
Python 2.5.1 (r251:54863, Feb  6 2009, 19:02:12) 
[GCC 4.0.1 (Apple Inc. build 5465)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from etsy import Etsy
>>> api = Etsy('YOUR-API-KEY-HERE')
>>> api.getFrontFeaturedListings(offset=10, limit=1)[0]['title']
'Artists Eco Journal -  Landscape Watercolor - Rustic Vegan Hemp and Recycled Rubber'
</pre>


See also [this blog post](http://codeascraft.etsy.com/2010/04/22/announcing-etsys-new-api/)
on Code as Craft.


## Configuration

For convenience (and to avoid storing API keys in revision control
systems), the package supports local configuration. You can manage
your API keys in a file called $HOME/etsy/keys (or the equivalent on
Windows) with the following format:

<pre>
v2 = 'Etsy API version 2 key goes here'
</pre>

Alternatively, you can specify a different key file when creating an API object.

<pre>
from etsy import Etsy

api = Etsy(key_file='/usr/share/etsy/keys')
</pre>

(Implementation note: the keys file can be any valid python script that defines
a module-level variable for the API version you are trying to use.)

## Tests

This package comes with a reasonably complete unit test suite. In order to run
the tests, use:

<pre>
$ python setup.py test
</pre>

Some of the tests (those that actually call the Etsy API) require your API key
to be locally configured. See the Configuration section, above.


## Method Table Caching

This module is implemented by metaprogramming against the method table published
by the Etsy API. In other words, API methods are not explicitly declared by the
code in this module. Instead, the list of allowable methods is downloaded and 
the patched into the API objects at runtime.

This has advantages and disadvantages. It allows the module to automatically 
receive new features, but on the other hand, this process is not as fast as 
explicitly declared methods. 

In order to speed things up, the method table json is cached locally by default.
If a $HOME/etsy directory exists, the cache file is created there. Otherwise, it 
is placed in the machine's temp directory. By default, this cache lasts 24 hours.

The cache file can be specified when creating an API object:

<pre>
from etsy import Etsy

api = Etsy(method_cache='myfile.json')
</pre>

Method table caching can also be disabled by passing None as the cache parameter:

<pre>
from etsy import Etsy

# do not cache methods
api = Etsy(method_cache=None)
</pre>


## Version History



### Version 0.3 
* Support for Etsy API v2 thanks to [Marc Abramowitz](http://marc-abramowitz.com). 
* Removed support for now-dead Etsy API v1. 


### Version 0.2.1 
* Added a cache for the method table json.
* Added a logging facility.


### Version 0.2 - 05-31-2010
* Added local configuration (~/.etsy) to eliminate cutting & pasting of api keys.
* Added client-side type checking for parameters.
* Added support for positional arguments.
* Added a test suite.
* Began differentiation between API versions.
* Added module to PyPI. 

### Version 0.1 - 05-24-2010 
Initial release