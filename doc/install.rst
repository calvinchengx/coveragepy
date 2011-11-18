.. _install:

============
Installation
============

:history: 20100725T225600, new for 3.4.
:history: 20100820T151500, updated for 3.4b1.
:history: 20100906T134800, updated for 3.4b2.
:history: 20110604T213400, updated for 3.5b1.
:history: 20110629T082400, updated for 3.5.
:history: 20110923T081900, updated for 3.5.1.


.. highlight:: console
.. _coverage_pypi: http://pypi.python.org/pypi/coverage


Installing coverage.py is fairly standard:

#.  Download the appropriate kit from the
    `coverage page on the Python Package Index`__.

#.  Run ``python setup.py install``.

or, use::

    $ easy_install coverage

or even::

    $ pip install coverage

.. __: coverage_pypi_


Installing from source
----------------------

Coverage.py includes a C extension for speed. If you are installing from source,
you may need to install the python-dev support files, for example with::

    $ sudo apt-get install python-dev


Installing on Windows
---------------------

For Windows, kits are provided on the `PyPI page`__ for different versions of
Python and different CPU architectures. These kits require that `setuptools`_ be
installed as a pre-requisite, but otherwise are self-contained.  They have the
C extension pre-compiled so there's no need to worry about compilers.

.. __: coverage_pypi_
.. _setuptools: http://pypi.python.org/pypi/setuptools


Checking the installation
-------------------------

If all went well, you should be able to open a command prompt, and see
coverage installed properly::

    $ coverage --version
    Coverage.py, version 3.5.1.  http://nedbatchelder.com/code/coverage

