===========
Quick Start
===========

This guide will help you get started with psqlc quickly.

First Command
=============

Let's start by listing all databases on your PostgreSQL server:

.. code-block:: bash

   psqlc show dbs -U postgres -P yourpassword

Output example:

.. code-block:: text

   ┏━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
   ┃ Database    ┃ Size   ┃ Encoding ┃ Collation     ┃
   ┡━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
   │ postgres    │ 8 MB   │ UTF8     │ en_US.UTF-8   │
   │ myapp       │ 45 MB  │ UTF8     │ en_US.UTF-8   │
   │ testdb      │ 12 MB  │ UTF8     │ en_US.UTF-8   │
   └─────────────┴────────┴──────────┴───────────────┘

Common Workflows
================

1. Create New User and Database
--------------------------------

Create a new PostgreSQL user and database:

.. code-block:: bash

   psqlc create newuser newpassword newdb -U postgres -P adminpass

This command will:

* Create user 'newuser' with password 'newpassword'
* Grant appropriate privileges
* Create database 'newdb'
* Set proper ownership

**Auto-detection from Django settings:**

If you have a Django project with settings.py:

.. code-block:: bash

   psqlc create -U postgres -P adminpass

psqlc will automatically read database configuration from your Django settings.

2. View Database Information
-----------------------------

**List all tables:**

.. code-block:: bash

   psqlc show tables -d mydb

**Show table structure:**

.. code-block:: bash

   psqlc describe -d mydb -t users

Output example:

.. code-block:: text

   ┏━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┓
   ┃ Column    ┃ Type       ┃ Max Length ┃ Nullable ┃ Default  ┃
   ┡━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━┩
   │ id        │ integer    │ -          │ NO       │ nextval()│
   │ username  │ varchar    │ 150        │ NO       │ -        │
   │ email     │ varchar    │ 254        │ YES      │ -        │
   │ created_at│ timestamp  │ -          │ NO       │ now()    │
   └───────────┴────────────┴────────────┴──────────┴──────────┘

**View database sizes:**

.. code-block:: bash

   psqlc show size -d mydb

**View all indexes:**

.. code-block:: bash

   psqlc show indexes -d mydb -t users

3. Execute Queries
------------------

**Simple SELECT query:**

.. code-block:: bash

   psqlc query -d mydb -q "SELECT * FROM users LIMIT 5"

**With read-only protection:**

.. code-block:: bash

   psqlc query -d mydb -q "SELECT * FROM orders" --readonly

This prevents accidental destructive operations.

**With custom row limit:**

.. code-block:: bash

   psqlc query -d mydb -q "SELECT * FROM logs" --limit 50

4. Monitor Connections
----------------------

View active database connections:

.. code-block:: bash

   psqlc show connections

Output shows:

* Database name
* Connected users
* Client IP addresses
* Connection states
* Query start times

5. Manage Users
---------------

**List all database users:**

.. code-block:: bash

   psqlc show users

**Drop a user:**

.. code-block:: bash

   psqlc drop user -u olduser

**Safety feature:** You'll be prompted to type the username to confirm.

6. Database Backup
------------------

Generate backup command:

.. code-block:: bash

   psqlc backup -d mydb

This generates a timestamp-based backup command like:

.. code-block:: bash

   pg_dump -h localhost -p 5432 -U postgres -d mydb -F p -f mydb_backup_20250114_153045.sql

Using Auto-Detection
====================

psqlc can automatically detect database configuration from various sources:

From Django Settings
--------------------

If you're in a Django project directory:

.. code-block:: bash

   # psqlc will auto-detect settings.py
   psqlc show tables

From .env Files
---------------

Create a .env file:

.. code-block:: bash

   POSTGRESQL_HOST=localhost
   POSTGRESQL_PORT=5432
   POSTGRESQL_USER=myuser
   POSTGRESQL_PASSWORD=mypassword
   POSTGRESQL_DB=mydb

Then simply run:

.. code-block:: bash

   psqlc show tables

From JSON/YAML Config
---------------------

Create config.json:

.. code-block:: json

   {
       "ENGINE": "postgresql",
       "HOST": "localhost",
       "PORT": 5432,
       "USER": "myuser",
       "PASSWORD": "mypassword",
       "NAME": "mydb"
   }

psqlc will automatically find and use it.

Command-Line Options
====================

Global Options
--------------

Available for all commands:

.. code-block:: bash

   -H, --hostname    PostgreSQL server address (default: 127.0.0.1)
   -U, --user        PostgreSQL superuser (default: postgres)
   -P, --passwd      PostgreSQL superuser password
   --port            PostgreSQL server port (default: 5432)
   --debug           Enable debug mode
   -v, --version     Show version

Database-Specific Options
--------------------------

For commands that work with specific databases:

.. code-block:: bash

   -d, --database    Database name
   -t, --table       Table name
   -q, --query       SQL query to execute
   --readonly        Prevent destructive operations
   --limit           Limit number of rows displayed

Examples with Options
---------------------

**Connect to remote server:**

.. code-block:: bash

   psqlc show dbs -H db.example.com -U admin -P secret --port 5433

**Use specific database:**

.. code-block:: bash

   psqlc show tables -d production_db -H db.example.com

**Debug mode:**

.. code-block:: bash

   psqlc show tables -d mydb --debug

Best Practices
==============

1. **Use Environment Variables**

   Store sensitive information in .env files instead of command line:

   .. code-block:: bash

      # .env
      POSTGRESQL_PASSWORD=secret123
      
      # Command line (no password needed)
      psqlc show dbs

2. **Use Read-Only Mode**

   For SELECT queries, use --readonly to prevent accidents:

   .. code-block:: bash

      psqlc query -d prod_db -q "SELECT * FROM users" --readonly

3. **Limit Output**

   For large tables, always use --limit:

   .. code-block:: bash

      psqlc query -d mydb -q "SELECT * FROM logs" --limit 100

4. **Backup Before Changes**

   Always backup before dropping databases or users:

   .. code-block:: bash

      psqlc backup -d mydb
      # Then run the generated pg_dump command
      psqlc drop database -d mydb

5. **Use Auto-Detection**

   Keep configuration files in your project directory for automatic detection.

Quick Reference
===============

.. code-block:: bash

   # Show Commands
   psqlc show dbs                    # List databases
   psqlc show tables -d mydb         # List tables
   psqlc show users                  # List users
   psqlc show connections            # Active connections
   psqlc show indexes -d mydb        # Show indexes
   psqlc show size -d mydb          # Database/table sizes

   # Create Commands
   psqlc create user pass db         # Create user & database

   # Query Commands
   psqlc describe -d mydb -t users   # Table structure
   psqlc query -d mydb -q "SQL"      # Execute query

   # Backup Commands
   psqlc backup -d mydb              # Generate backup command

   # Drop Commands
   psqlc drop database -d mydb       # Drop database
   psqlc drop user -u username       # Drop user

Next Steps
==========

* :doc:`commands` - Explore all available commands in detail
* :doc:`configuration` - Learn about advanced configuration options
* :doc:`examples` - See real-world usage examples
* :doc:`api/modules` - API reference for programmatic usage