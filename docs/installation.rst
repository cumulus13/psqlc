============
Installation
============

System Requirements
===================

Before installing psqlc, ensure your system meets these requirements:

**Operating Systems:**

* Linux (Ubuntu, Debian, CentOS, etc.)
* macOS 10.12 or later
* Windows 10 or later

**Python Version:**

* Python 3.6 or higher
* pip package manager

**PostgreSQL:**

* PostgreSQL 9.6 or higher
* Access to PostgreSQL server (local or remote)

Installation Methods
====================

Using pip (Recommended)
-----------------------

The easiest way to install psqlc is using pip:

.. code-block:: bash

   pip install psqlc

To upgrade to the latest version:

.. code-block:: bash

   pip install --upgrade psqlc

From Source
-----------

To install from source code:

.. code-block:: bash

   git clone https://github.com/cumulus13/psqlc.git
   cd psqlc
   pip install -e .

Development Installation
------------------------

For development with all dependencies:

.. code-block:: bash

   git clone https://github.com/cumulus13/psqlc.git
   cd psqlc
   pip install -e ".[dev]"

This installs additional development tools like:

* pytest (for testing)
* black (for code formatting)
* flake8 (for linting)
* sphinx (for documentation)

Dependencies
============

psqlc automatically installs these dependencies:

Core Dependencies
-----------------

* **rich** - Beautiful terminal output formatting
* **asyncpg** - High-performance PostgreSQL client library
* **licface** - Custom argument parser with rich formatting
* **envdot** - Environment and configuration file parser
* **pwinput** - Secure password input

.. code-block:: bash

   pip install rich asyncpg licface envdot pwinput

Optional Dependencies
---------------------

For documentation building:

.. code-block:: bash

   pip install sphinx sphinx_rtd_theme sphinx-copybutton myst-parser

Verifying Installation
======================

After installation, verify that psqlc is installed correctly:

.. code-block:: bash

   psqlc --version

You should see output like:

.. code-block:: text

   📦 Version: 2.0

Check available commands:

.. code-block:: bash

   psqlc --help

Configuration Files
===================

psqlc can automatically detect configuration from:

1. **Django settings.py** - Automatically detects Django database configuration
2. **.env files** - Environment variables
3. **.json files** - JSON configuration
4. **.yaml files** - YAML configuration

Example .env file:

.. code-block:: bash

   # PostgreSQL Configuration
   POSTGRESQL_HOST=localhost
   POSTGRESQL_PORT=5432
   POSTGRESQL_USER=myuser
   POSTGRESQL_PASSWORD=mypassword
   POSTGRESQL_DB=mydb

Example settings.py (Django):

.. code-block:: python

   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'mydb',
           'USER': 'myuser',
           'PASSWORD': 'mypassword',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }

Troubleshooting
===============

Common Issues
-------------

**Issue: Command not found**

If you get "psqlc: command not found", ensure pip's bin directory is in your PATH:

.. code-block:: bash

   # For Linux/macOS
   export PATH="$HOME/.local/bin:$PATH"
   
   # For Windows, add to PATH:
   # C:\Users\YourUsername\AppData\Local\Programs\Python\Python3X\Scripts

**Issue: Cannot connect to PostgreSQL**

Ensure PostgreSQL is running:

.. code-block:: bash

   # Linux
   sudo systemctl status postgresql
   
   # macOS (with Homebrew)
   brew services list
   
   # Windows
   # Check Services app for PostgreSQL service

**Issue: Permission denied**

On Linux/macOS, you might need to install with sudo or use a virtual environment:

.. code-block:: bash

   # Use virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   
   pip install psqlc

**Issue: Module import errors**

Reinstall dependencies:

.. code-block:: bash

   pip install --upgrade --force-reinstall psqlc

Uninstallation
==============

To remove psqlc from your system:

.. code-block:: bash

   pip uninstall psqlc

To remove including configuration files:

.. code-block:: bash

   pip uninstall psqlc
   rm -rf ~/.psqlc  # If any config files exist

Next Steps
==========

Now that you have psqlc installed, check out:

* :doc:`quickstart` - Get started with basic commands
* :doc:`configuration` - Learn about configuration options
* :doc:`commands` - Explore all available commands
* :doc:`examples` - See practical usage examples