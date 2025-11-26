=========
Changelog
=========

Version 1.0.6 (2025-11-20)
========================

Major Release
-------------

New Features
~~~~~~~~~~~~

* Complete rewrite with asyncpg for high-performance operations
* Rich-formatted table output with colors
* Intelligent auto-detection of Django settings
* Support for .env, .json, and .yaml configuration files
* Interactive confirmations for destructive operations
* Read-only mode for safe query execution
* Comprehensive error handling

Commands Added
~~~~~~~~~~~~~~

* ``show dbs`` - List all databases with sizes
* ``show tables`` - List tables with statistics
* ``show users`` - Display all database users
* ``show connections`` - Monitor active connections
* ``show indexes`` - View table indexes
* ``show size`` - Database and table size analysis
* ``create`` - Create user and database with auto-detection
* ``describe`` - Show detailed table structure
* ``query`` - Execute SQL with safety features
* ``backup`` - Generate backup commands
* ``drop database`` - Safely drop databases
* ``drop user`` - Safely drop users

Improvements
~~~~~~~~~~~~

* Production-ready error handling
* Password prompts for security
* Debug mode for troubleshooting
* Recursive configuration file search
* Environment variable support
* Multiple database engine detection

Version 1.0 (2024-10-14)
========================

Initial Release
---------------

* Basic PostgreSQL connection management
* Simple database creation
* User management features
* Basic query execution