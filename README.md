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

There are currently two versions of the Etsy API, v1 and v2. This library will work
with both versions. The basic interface to either API is the same, although many
of the methods are different. You can start using the v2 API by using an import 
like this:

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


## Version History

### Version 0.2 - in progress
* Added support for the v2 API
* Added local configuration (~/.etsy) to eliminate cutting & pasting of api keys.
* Added a test suite.
* Added module to PyPI. 

### Version 0.1 - 05-24-2010 
Initial release