===========
API Modules
===========

.. automodule:: psqlc
   :members:
   :undoc-members:
   :show-inheritance:

Core Functions
==============

Connection Management
---------------------

.. autofunction:: psqlc.get_connection

.. autofunction:: psqlc.get_db_config_or_args

Configuration
-------------

.. autofunction:: psqlc.parse_django_settings

.. autofunction:: psqlc.find_settings_recursive

.. autofunction:: psqlc.load_settings_from_path

Database Operations
-------------------

.. autofunction:: psqlc.show_databases

.. autofunction:: psqlc.show_tables

.. autofunction:: psqlc.show_users

.. autofunction:: psqlc.show_connections

.. autofunction:: psqlc.show_indexes

.. autofunction:: psqlc.show_size

Query Operations
----------------

.. autofunction:: psqlc.describe_table

.. autofunction:: psqlc.execute_query

Management Operations
---------------------

.. autofunction:: psqlc.create_user_db

.. autofunction:: psqlc.drop_database

.. autofunction:: psqlc.drop_user

.. autofunction:: psqlc.backup_database

Utility Functions
-----------------

.. autofunction:: psqlc.rich_print

.. autofunction:: psqlc.print_exception

.. autofunction:: psqlc.get_version