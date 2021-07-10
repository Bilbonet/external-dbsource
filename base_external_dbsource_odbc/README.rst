.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

===============================
External Database Source - ODBC
===============================

This module extends ``base_external_dbsource``, allowing you to connect to
foreign ODBC databases using PyODBC.



Installation
============

* Install ``unixodbc`` and ``python-pyodbc`` packages

Configuration
=============

Database sources can be configured in Settings > Configuration -> Data sources.


Usage
=====

To use this module:

* Go to Settings > Database Structure > Database Sources
* Click on Create to enter the following information:

* Datasource name 
* Pasword
* Connector: Choose the database to which you want to connect
* Connection string: Specify how to connect to database


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Bilbonet/external-dbsource/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Daniel Reis <dreis.pt@hotmail.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Gervais Naoussi <gervaisnaoussi@gmail.com>
* Dave Lasley <dave@laslabs.com>

Maintainer
----------

This module is maintained by Bilbonet.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://github.com/Bilbonet.
