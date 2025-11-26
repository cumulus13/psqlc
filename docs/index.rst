.. psqlc documentation master file

========================================
psqlc - PostgreSQL Management CLI Tool
========================================

.. image:: https://img.shields.io/pypi/v/psqlc.svg
   :target: https://pypi.org/project/psqlc/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/psqlc.svg
   :target: https://pypi.org/project/psqlc/
   :alt: Python versions

.. image:: https://img.shields.io/github/license/cumulus13/psqlc.svg
   :target: https://github.com/cumulus13/psqlc/blob/main/LICENSE
   :alt: License

**psqlc** is a production-ready, feature-rich command-line interface tool for managing PostgreSQL databases with beautiful output formatting and intelligent auto-detection capabilities.

.. image:: _static/screenshot.png
   :alt: psqlc screenshot
   :align: center
   :width: 80%

Features
========

✨ **Key Features:**

* 🚀 **Async Operations** - Built on asyncpg for high-performance database operations
* 🎨 **Beautiful Output** - Rich-formatted tables and colored output for better readability
* 🔍 **Auto-Detection** - Intelligently detects Django settings and configuration files
* 🛡️ **Production-Ready** - Comprehensive error handling and safe operations
* 📊 **Comprehensive Management** - Full database, table, user, and query management
* 🔒 **Security-First** - Password prompts and confirmation for destructive operations
* 🌐 **Multi-Format Config** - Supports .env, .json, .yaml, and settings.py files

Quick Start
===========

Installation
------------

Install psqlc using pip:

.. code-block:: bash

   pip install psqlc

Requirements
------------

* Python 3.6+
* PostgreSQL database server
* Required packages: rich, asyncpg, licface, envdot, pwinput

Basic Usage
-----------

Show all databases:

.. code-block:: bash

   psqlc show dbs -U postgres -P yourpassword

Create user and database:

.. code-block:: bash

   psqlc create myuser mypassword mydb -U postgres -P adminpass

Show tables in database:

.. code-block:: bash

   psqlc show tables -d mydb

Execute query:

.. code-block:: bash

   psqlc query -d mydb -q "SELECT * FROM users LIMIT 10"

Table of Contents
=================

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   configuration
   commands
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/modules
   api/functions
   api/utilities

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   changelog
   contributing
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Links
=====

* **GitHub Repository**: https://github.com/cumulus13/psqlc
* **PyPI Package**: https://pypi.org/project/psqlc/
* **Issue Tracker**: https://github.com/cumulus13/psqlc/issues
* **Author**: Hadi Cahyadi <cumulus13@gmail.com>

License
=======

This project is licensed under the MIT License - see the LICENSE file for details.

Author
======

**Hadi Cahyadi**

* Email: cumulus13@gmail.com
* GitHub: https://github.com/cumulus13