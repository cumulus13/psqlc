========
Examples
========

Real-World Usage Examples
=========================

Django Project Setup
--------------------

Setting up PostgreSQL for a new Django project:

.. code-block:: bash

   # 1. Create user and database
   cd /path/to/django/project
   psqlc create -U postgres -P adminpass
   
   # 2. Verify tables after migration
   python manage.py migrate
   psqlc show tables
   
   # 3. Check database size
   psqlc show size

Production Database Management
-------------------------------

Managing a production database:

.. code-block:: bash

   # 1. Check active connections
   psqlc show connections -H prod.example.com -U admin
   
   # 2. Monitor database sizes
   psqlc show size -H prod.example.com
   
   # 3. Execute read-only query
   psqlc query -d production \\
       -q "SELECT COUNT(*) FROM orders WHERE created_at > NOW() - INTERVAL '1 day'" \\
       --readonly
   
   # 4. Create backup before maintenance
   psqlc backup -d production
   # Then run the generated pg_dump command

Data Analysis
-------------

Quick data analysis queries:

.. code-block:: bash

   # Get user statistics
   psqlc query -d analytics -q "
       SELECT 
           DATE(created_at) as date,
           COUNT(*) as user_count,
           COUNT(DISTINCT country) as countries
       FROM users 
       WHERE created_at > NOW() - INTERVAL '30 days'
       GROUP BY DATE(created_at)
       ORDER BY date DESC
   " --limit 50

   # Check table relationships
   psqlc describe -d mydb -t orders
   psqlc describe -d mydb -t order_items
   psqlc show indexes -d mydb -t orders

Database Migration
------------------

Migrating from development to production:

.. code-block:: bash

   # 1. Backup development database
   psqlc backup -d dev_db
   pg_dump -h localhost -U postgres -d dev_db -F c -f dev_backup.dump
   
   # 2. Create production user and database
   psqlc create prod_user prod_pass prod_db -H prod.server.com -U postgres
   
   # 3. Restore to production
   pg_restore -h prod.server.com -U prod_user -d prod_db dev_backup.dump
   
   # 4. Verify migration
   psqlc show tables -H prod.server.com -d prod_db
   psqlc show size -H prod.server.com -d prod_db

Multi-Database Management
--------------------------

Managing multiple databases:

.. code-block:: bash

   # Create script for multiple databases
   cat > manage_databases.sh << 'EOF'
   #!/bin/bash
   DATABASES=("app1_db" "app2_db" "app3_db")
   
   for db in "${DATABASES[@]}"; do
       echo "=== Database: $db ==="
       psqlc show size -d "$db"
       psqlc show connections -d "$db"
       echo ""
   done
   EOF
   
   chmod +x manage_databases.sh
   ./manage_databases.sh

Performance Monitoring
----------------------

Monitor database performance:

.. code-block:: bash

   # Check table sizes and identify large tables
   psqlc show size -d mydb
   
   # View all indexes
   psqlc show indexes -d mydb
   
   # Check for missing indexes on specific table
   psqlc query -d mydb -q "
       SELECT 
           schemaname,
           tablename,
           attname,
           n_distinct,
           correlation
       FROM pg_stats
       WHERE tablename = 'large_table'
       ORDER BY n_distinct DESC
   "

Automated Backup Script
-----------------------

Create automated backup routine:

.. code-block:: bash

   cat > backup_all.sh << 'EOF'
   #!/bin/bash
   # Backup all databases
   
   BACKUP_DIR="/backups/postgresql"
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   
   # Get list of databases
   DATABASES=$(psqlc show dbs -U postgres -P $PG_PASSWORD | grep -v "Database" | grep -v "━" | awk '{print $1}')
   
   mkdir -p "$BACKUP_DIR/$TIMESTAMP"
   
   for db in $DATABASES; do
       if [[ "$db" != "postgres" && "$db" != "template0" && "$db" != "template1" ]]; then
           echo "Backing up: $db"
           pg_dump -U postgres -d "$db" -F c -f "$BACKUP_DIR/$TIMESTAMP/${db}.dump"
           
           # Get size info
           psqlc show size -d "$db" > "$BACKUP_DIR/$TIMESTAMP/${db}_info.txt"
       fi
   done
   
   echo "Backup completed: $BACKUP_DIR/$TIMESTAMP"
   EOF
   
   chmod +x backup_all.sh

Development Workflow
--------------------

Typical development workflow:

.. code-block:: bash

   # 1. Start new feature branch with fresh database
   git checkout -b feature/new-feature
   psqlc create feature_user feature_pass feature_db
   
   # 2. Update Django settings or .env file
   # 3. Run migrations
   python manage.py migrate
   
   # 4. Verify database structure
   psqlc show tables -d feature_db
   psqlc describe -d feature_db -t new_model
   
   # 5. Test queries
   psqlc query -d feature_db -q "SELECT * FROM new_model LIMIT 5"
   
   # 6. After feature is complete, cleanup
   psqlc drop database -d feature_db
   psqlc drop user -u feature_user

CI/CD Integration
-----------------

Integrate with CI/CD pipeline:

.. code-block:: yaml

   # .gitlab-ci.yml or similar
   test_database:
     script:
       - pip install psqlc
       - psqlc create test_user test_pass test_db -U postgres -P $PG_PASSWORD
       - psqlc show tables -d test_db
       - python manage.py migrate
       - python manage.py test
       - psqlc drop database -d test_db
       - psqlc drop user -u test_user

Docker Integration
------------------

Use with Docker PostgreSQL:

.. code-block:: bash

   # docker-compose.yml
   version: '3.8'
   services:
     postgres:
       image: postgres:15
       environment:
         POSTGRES_PASSWORD: devpassword
       ports:
         - "5432:5432"
   
   # Start container
   docker-compose up -d
   
   # Wait for PostgreSQL to be ready
   sleep 5
   
   # Create database
   psqlc create myuser mypass mydb -U postgres -P devpassword
   
   # Use it
   psqlc show tables -d mydb

Troubleshooting Common Issues
==============================

Connection Issues
-----------------

.. code-block:: bash

   # Test connection
   psqlc show dbs -U postgres -P yourpassword --debug
   
   # Check PostgreSQL is running
   sudo systemctl status postgresql  # Linux
   brew services list                # macOS
   
   # Verify pg_hba.conf allows connections
   # On Linux: /etc/postgresql/*/main/pg_hba.conf

Permission Issues
-----------------

.. code-block:: bash

   # Grant missing permissions
   psqlc query -d postgres -q "
       GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;
       GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myuser;
   "

Large Database Queries
----------------------

.. code-block:: bash

   # Use LIMIT for large tables
   psqlc query -d mydb -q "SELECT * FROM large_table" --limit 10
   
   # Export to file instead
   psqlc query -d mydb -q "SELECT * FROM large_table" > output.txt

Performance Tips
================

1. **Use indexes** - Check missing indexes:

   .. code-block:: bash

      psqlc show indexes -d mydb

2. **Monitor connections** - Close idle connections:

   .. code-block:: bash

      psqlc show connections

3. **Regular backups** - Automate with cron:

   .. code-block:: bash

      0 2 * * * /path/to/backup_all.sh

4. **Analyze queries** - Use EXPLAIN:

   .. code-block:: bash

      psqlc query -d mydb -q "EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com'"