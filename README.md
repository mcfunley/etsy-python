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


## Compatibility

*Draft - v2 API support not implemented yet.*

There are currently two versions of the Etsy API, v1 and v2. This
library works with both versions. The basic interface to either API is
the same, although many of the methods are different. In order to use
the v2 API,

<pre>
from etsy import EtsyV2 as Etsy
</pre>

At some point, the v2 API will replace the v1 API as the default. Therefore you 
may want to import the v1 API explicitly, like this:

<pre>
from etsy import EtsyV1 as Etsy
</pre>

See also [this blog post](http://codeascraft.etsy.com/2010/04/22/announcing-etsys-new-api/)
on Code as Craft.


## Configuration

For convenience (and to avoid storing API keys in revision control
systems), the package supports local configuration. You can manage
your API keys in a file called $HOME/etsy/keys (or the equivalent on
Windows) with the following format:

<pre>
v1 = 'Etsy API version 1 key goes here'
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


## Future Work

Currently, the API objects download the method tables from etsy.com upon module load.
While this is fine for persistent or long-running applications, it is not ideal for
short-lived programs where the cost of such an operation becomes very significant. 
There will be enhancements in the future to address this problem in a number of ways.

## Version History

### Version 0.2 - in progress
* Added local configuration (~/.etsy) to eliminate cutting & pasting of api keys.
* Added client-side type checking for parameters.
* Added support for positional arguments.
* Added a test suite.
* Began differentiation between API versions.
* Added module to PyPI. 

### Version 0.1 - 05-24-2010 
Initial release