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


## Configuration


## Version History

### Version 0.2 
* 05-30-2010 - Added support for the v2 API, configuration, and tests.

### Version 0.1
* 05-24-2010 - Initial release