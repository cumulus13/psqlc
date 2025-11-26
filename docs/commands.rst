========
Commands
========

This page provides detailed documentation for all psqlc commands.

Command Overview
================

psqlc commands are organized into categories:

* **Show Commands** - Display database information
* **Create Commands** - Create users and databases
* **Query Commands** - Execute SQL and describe tables
* **Backup Commands** - Database backup operations
* **Drop Commands** - Remove databases and users

Show Commands
=============

show dbs
--------

List all databases on the PostgreSQL server.

**Syntax:**

.. code-block:: bash

   psqlc show dbs [OPTIONS]

**Options:**

* ``-H, --hostname TEXT`` - PostgreSQL server address (default: 127.0.0.1)
* ``-U, --user TEXT`` - PostgreSQL superuser (default: postgres)
* ``-P, --passwd TEXT`` - PostgreSQL superuser password
* ``--port INTEGER`` - PostgreSQL server port (default: 5432)

**Examples:**

.. code-block:: bash

   # List all databases
   psqlc show dbs -U postgres -P mypassword

   # Connect to remote server
   psqlc show dbs -H db.example.com -U admin -P secret

**Output:**

.. code-block:: text

   ┏━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
   ┃ Database    ┃ Size   ┃ Encoding ┃ Collation     ┃
   ┡━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
   │ postgres    │ 8 MB   │ UTF8     │ en_US.UTF-8   │
   │ myapp       │ 45 MB  │ UTF8     │ en_US.UTF-8   │
   └─────────────┴────────┴──────────┴───────────────┘

show tables
-----------

List all tables in a database.

**Syntax:**

.. code-block:: bash

   psqlc show tables [OPTIONS]

**Options:**

* ``-d, --database TEXT`` - Database name (auto-detects if not provided)
* ``-H, --hostname TEXT`` - PostgreSQL server address
* ``-U, --user TEXT`` - PostgreSQL user
* ``-P, --passwd TEXT`` - PostgreSQL password
* ``--port INTEGER`` - PostgreSQL port
* ``--debug`` - Enable debug mode

**Examples:**

.. code-block:: bash

   # List tables in specific database
   psqlc show tables -d mydb

   # Auto-detect from Django settings
   psqlc show tables

   # With debug info
   psqlc show tables -d mydb --debug

**Output:**

.. code-block:: text

   ┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┓
   ┃ Schema ┃ Table      ┃ Size   ┃ Columns ┃
   ┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━┩
   │ public │ users      │ 128 kB │ 8       │
   │ public │ orders     │ 256 kB │ 12      │
   │ public │ products   │ 64 kB  │ 6       │
   └────────┴────────────┴────────┴─────────┘

show users
----------

List all database users/roles.

**Syntax:**

.. code-block:: bash

   psqlc show users [OPTIONS]

**Examples:**

.. code-block:: bash

   psqlc show users -U postgres -P mypassword

**Output:**

.. code-block:: text

   ┏━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
   ┃ Username ┃ Superuser ┃ Create DB ┃ Create Role ┃ Can Login┃ Replication ┃
   ┡━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
   │ postgres │ True      │ True      │ True        │ True     │ True        │
   │ myuser   │ False     │ True      │ False       │ True     │ False       │
   └──────────┴───────────┴───────────┴─────────────┴──────────┴─────────────┘

show connections
----------------

Display active database connections.

**Syntax:**

.. code-block:: bash

   psqlc show connections [OPTIONS]

**Examples:**

.. code-block:: bash

   psqlc show connections -U postgres -P mypassword

**Output:**

.. code-block:: text

   ┏━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
   ┃ Database ┃ User    ┃ Client       ┃ State  ┃ Query Start        ┃
   ┡━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
   │ myapp    │ appuser │ 192.168.1.10 │ active │ 2025-01-14 10:30:15│
   │ myapp    │ admin   │ 127.0.0.1    │ idle   │ 2025-01-14 10:25:00│
   └──────────┴─────────┴──────────────┴────────┴────────────────────┘

show indexes
------------

Show indexes in a table or database.

**Syntax:**

.. code-block:: bash

   psqlc show indexes [OPTIONS]

**Options:**

* ``-d, --database TEXT`` - Database name (required)
* ``-t, --table TEXT`` - Table name (optional, shows all if not specified)

**Examples:**

.. code-block:: bash

   # Show all indexes in database
   psqlc show indexes -d mydb

   # Show indexes for specific table
   psqlc show indexes -d mydb -t users

**Output (all indexes):**

.. code-block:: text

   ┏━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ Schema ┃ Table   ┃ Index Name      ┃ Definition                 ┃
   ┡━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
   │ public │ users   │ users_pkey      │ CREATE UNIQUE INDEX...     │
   │ public │ users   │ users_email_idx │ CREATE INDEX ON users...   │
   └────────┴─────────┴─────────────────┴────────────────────────────┘

show size
---------

Show database or table sizes.

**Syntax:**

.. code-block:: bash

   psqlc show size [OPTIONS]

**Options:**

* ``-d, --database TEXT`` - Database name (optional)
* ``-t, --table TEXT`` - Table name (optional)

**Examples:**

.. code-block:: bash

   # Show all database sizes
   psqlc show size

   # Show table sizes in database
   psqlc show size -d mydb

   # Show specific table size
   psqlc show size -d mydb -t users

**Output (all databases):**

.. code-block:: text

   ┏━━━━━━━━━━━━━┳━━━━━━━━━┓
   ┃ Database    ┃ Size    ┃
   ┡━━━━━━━━━━━━━╇━━━━━━━━━┩
   │ postgres    │ 8 MB    │
   │ myapp       │ 145 MB  │
   │ testdb      │ 12 MB   │
   └─────────────┴─────────┘

   📊 Total Size: 0.16 GB

**Output (specific table):**

.. code-block:: text

   📊 Size of table 'users':
      Total Size:   2048 kB
      Table Size:   1536 kB
      Indexes Size: 512 kB

Create Commands
===============

create
------

Create PostgreSQL user and database.

**Syntax:**

.. code-block:: bash

   psqlc create [USERNAME PASSWORD DATABASE] [OPTIONS]

**Positional Arguments:**

* ``USERNAME`` - New PostgreSQL username
* ``PASSWORD`` - Password for new user
* ``DATABASE`` - Database name to create

**Options:**

* ``-u, --username TEXT`` - New PostgreSQL username (alternative)
* ``-p, --password TEXT`` - Password for new user (alternative)
* ``-d, --database TEXT`` - Database name to create (alternative)
* ``-U, --user TEXT`` - PostgreSQL superuser (default: postgres)
* ``-P, --passwd TEXT`` - Superuser password
* ``-H, --hostname TEXT`` - PostgreSQL server address
* ``--port INTEGER`` - PostgreSQL server port

**Examples:**

.. code-block:: bash

   # Create with positional arguments
   psqlc create myuser mypass mydb -U postgres -P adminpass

   # Create with named options
   psqlc create -u myuser -p mypass -d mydb -U postgres -P adminpass

   # Auto-detect from Django settings.py
   psqlc create -U postgres -P adminpass

   # Auto-detect from config file path
   psqlc create /path/to/settings.py -U postgres -P adminpass

**What it does:**

1. Creates new PostgreSQL user with specified password
2. Grants LOGIN, CREATEDB, REPLICATION, BYPASSRLS privileges
3. Creates new database
4. Sets proper ownership and permissions

**Interactive behavior:**

If database already exists, you'll be prompted:

.. code-block:: text

   ⚠️ Database 'mydb' already exists.
   ✓ Drop and recreate 'mydb'? [y/N]:

Query Commands
==============

describe
--------

Show table structure with columns, types, and constraints.

**Syntax:**

.. code-block:: bash

   psqlc describe [OPTIONS]

**Options:**

* ``-d, --database TEXT`` - Database name (auto-detects if not provided)
* ``-t, --table TEXT`` - Table name (required)

**Examples:**

.. code-block:: bash

   # Describe table
   psqlc describe -d mydb -t users

   # Auto-detect database
   psqlc describe -t users

**Output:**

.. code-block:: text

   ┏━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
   ┃ Column    ┃ Type       ┃ Max Length ┃ Nullable ┃ Default       ┃
   ┡━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
   │ id        │ integer    │ -          │ NO       │ nextval(...)  │
   │ username  │ varchar    │ 150        │ NO       │ -             │
   │ email     │ varchar    │ 254        │ YES      │ -             │
   │ is_active │ boolean    │ -          │ NO       │ true          │
   │ created_at│ timestamp  │ -          │ NO       │ now()         │
   └───────────┴────────────┴────────────┴──────────┴───────────────┘

query
-----

Execute custom SQL query.

**Syntax:**

.. code-block:: bash

   psqlc query [OPTIONS]

**Options:**

* ``-d, --database TEXT`` - Database name (auto-detects if not provided)
* ``-q, --query TEXT`` - SQL query to execute (required)
* ``--readonly`` - Prevent destructive operations (recommended for SELECT)
* ``--limit INTEGER`` - Limit rows displayed (default: 100)

**Examples:**

.. code-block:: bash

   # Simple SELECT query
   psqlc query -d mydb -q "SELECT * FROM users LIMIT 5"

   # With read-only protection
   psqlc query -d mydb -q "SELECT * FROM orders" --readonly

   # Custom row limit
   psqlc query -d mydb -q "SELECT * FROM logs" --limit 50

   # UPDATE query (requires no --readonly flag)
   psqlc query -d mydb -q "UPDATE users SET is_active = true WHERE id = 1"

**Read-only mode:**

With ``--readonly`` flag, these operations are blocked:

* DROP
* DELETE
* TRUNCATE
* ALTER
* CREATE
* INSERT
* UPDATE

**Output (SELECT queries):**

.. code-block:: text

   ┏━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
   ┃ id ┃ username ┃ email               ┃ is_active ┃
   ┡━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
   │ 1  │ john     │ john@example.com    │ True      │
   │ 2  │ jane     │ jane@example.com    │ True      │
   └────┴──────────┴─────────────────────┴───────────┘

**Output (non-SELECT queries):**

.. code-block:: text

   ✅ Query executed successfully

Backup Commands
===============

backup
------

Generate backup command for database using pg_dump.

**Syntax:**

.. code-block:: bash

   psqlc backup [OPTIONS]

**Options:**

* ``-d, --database TEXT`` - Database name (auto-detects if not provided)

**Examples:**

.. code-block:: bash

   # Generate backup command
   psqlc backup -d mydb

   # Auto-detect database
   psqlc backup

**Output:**

.. code-block:: text

   🗄️ Creating backup of 'mydb'...
   💡 Run this command manually:
      pg_dump -h localhost -p 5432 -U postgres -d mydb -F p -f mydb_backup_20250114_153045.sql

**Notes:**

* The command generates a timestamp-based filename
* You need to run the generated pg_dump command manually
* Requires pg_dump to be installed on your system
* Format is plain SQL (-F p)

Drop Commands
=============

drop database
-------------

Drop a database with confirmation.

**Syntax:**

.. code-block:: bash

   psqlc drop database [OPTIONS]

**Options:**

* ``-d, --database TEXT`` - Database name (required)
* ``-U, --user TEXT`` - PostgreSQL superuser
* ``-P, --passwd TEXT`` - Superuser password

**Examples:**

.. code-block:: bash

   psqlc drop database -d olddb -U postgres -P adminpass

**Interactive confirmation:**

.. code-block:: text

   ⚠️  WARNING: You are about to DROP database 'olddb'
   ✓ Type the database name to confirm: olddb
   ✅ Database 'olddb' dropped successfully

**Safety features:**

* Requires typing the exact database name to confirm
* Automatically terminates all active connections to the database
* Cannot be undone - make backups first!

drop user
---------

Drop a user/role with confirmation.

**Syntax:**

.. code-block:: bash

   psqlc drop user [OPTIONS]

**Options:**

* ``-u, --username TEXT`` - Username to drop (required)
* ``-U, --user TEXT`` - PostgreSQL superuser
* ``-P, --passwd TEXT`` - Superuser password

**Examples:**

.. code-block:: bash

   psqlc drop user -u olduser -U postgres -P adminpass

**Interactive confirmation:**

.. code-block:: text

   ⚠️  WARNING: You are about to DROP user 'olduser'
   ✓ Type the username to confirm: olduser
   ✅ User 'olduser' dropped successfully

**Safety features:**

* Requires typing the exact username to confirm
* Cannot be undone
* May fail if user owns databases or objects

Global Options
==============

These options are available for most commands:

Connection Options
------------------

.. code-block:: bash

   -H, --hostname TEXT    # PostgreSQL server address (default: 127.0.0.1)
   -U, --user TEXT        # PostgreSQL user (default: postgres)
   -P, --passwd TEXT      # PostgreSQL password
   --port INTEGER         # PostgreSQL port (default: 5432)

Debug Options
-------------

.. code-block:: bash

   --debug               # Enable debug mode with verbose output
   -v, --version         # Show version information

Environment Variables
=====================

psqlc respects these environment variables:

.. code-block:: bash

   HOST                  # PostgreSQL hostname
   PORT                  # PostgreSQL port
   USER                  # PostgreSQL username
   PASSWORD              # PostgreSQL password
   DATABASE              # Database name
   DB_NAME               # Alternative database name
   DB                    # Alternative database name
   DEBUG                 # Enable debug mode (1/true/yes)
   TRACEBACK             # Show full tracebacks (1/true/yes)

Auto-Detection
==============

psqlc automatically searches for configuration in this order:

1. Command-line arguments
2. Environment variables
3. settings.py (Django)
4. .env file
5. .json file
6. .yaml file

The search is recursive up to 5 levels deep, excluding:

* node_modules
* venv
* __pycache__
* *-env directories

Error Handling
==============

psqlc provides clear error messages:

**Connection errors:**

.. code-block:: text

   ❌ Connection failed: FATAL: password authentication failed for user "postgres"

**Missing parameters:**

.. code-block:: text

   ❌ Database name required. Use -d/--database

**Invalid queries:**

.. code-block:: text

   ❌ Query error: syntax error at or near "SELEC"

**Destructive operations blocked:**

.. code-block:: text

   ❌ Destructive queries not allowed in read-only mode