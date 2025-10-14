# PostgreSQL Manager CLI Tool

A production-ready, feature-rich command-line interface tool for managing PostgreSQL databases with beautiful output formatting and intelligent auto-detection capabilities.

## ✨ Features

- 🎯 **Intuitive Sub-commands** - Natural command structure (e.g., `show dbs`, `show tables`)
- 🔍 **Auto-detection** - Automatically finds and parses Django `settings.py` files
- 🎨 **Beautiful Output** - Rich formatted tables with color-coded messages
- 🔐 **Security First** - Confirmation prompts for destructive operations, read-only mode for queries
- 📊 **Comprehensive Info** - Database sizes, table structures, indexes, connections, and more
- 🚀 **Production Ready** - Robust error handling, connection timeouts, transaction management

## 📋 Requirements

```bash
pip install psqlc
# or
pip install git+https://github.com/cumulus13/psqlc
```

## 🚀 Quick Start

### Basic Usage

```bash
# Show all databases
psqlc show dbs -U postgres -P password

# Show tables in a database
psqlc show tables -d mydb -U postgres

# Create user and database
psqlc create newuser newpass newdb -U postgres

# Execute a query
psqlc query -d mydb -q "SELECT * FROM users LIMIT 10" -U postgres
```

### Using Django Settings Auto-detection

If you have a Django `settings.py` file in your project, the tool will automatically detect and use the database configuration:

```bash
# No need to specify database credentials!
psqlc show tables
psqlc show dbs
psqlc describe -t users
```

The tool searches recursively (up to 5 levels deep) for `settings.py` files and extracts PostgreSQL configuration automatically.

## 📚 Commands Reference

### Global Options

These options can be used with any command:

| Option | Description | Default |
|--------|-------------|---------|
| `-H, --hostname` | PostgreSQL server address | `222.222.222.5` |
| `-U, --user` | PostgreSQL superuser | `postgres` |
| `-P, --passwd` | PostgreSQL superuser password | Auto-detect or prompt |
| `--port` | PostgreSQL server port | `5432` |
| `--debug` | Enable debug mode | `False` |

### SHOW Commands

Display various database information with beautiful formatted tables.

#### `show dbs`

List all databases with size and encoding information.

```bash
psqlc show dbs
```

**Output:**
```
┌─────────────┬─────────┬──────────┬──────────────┐
│ Database    │ Size    │ Encoding │ Collation    │
├─────────────┼─────────┼──────────┼──────────────┤
│ myapp_db    │ 125 MB  │ UTF8     │ en_US.UTF-8  │
│ testdb      │ 45 MB   │ UTF8     │ en_US.UTF-8  │
└─────────────┴─────────┴──────────┴──────────────┘
```

#### `show tables`

List all tables in a database with size and column count.

```bash
# Auto-detect database from settings.py
psqlc show tables

# Specify database explicitly
psqlc show tables -d mydb
```

**Options:**
- `-d, --database` - Database name (auto-detects from settings.py if not provided)

#### `show users`

List all PostgreSQL users/roles with their permissions.

```bash
psqlc show users
```

**Output:**
```
┌──────────────┬───────────┬───────────┬─────────────┬───────────┬──────────────┐
│ Username     │ Superuser │ Create DB │ Create Role │ Can Login │ Replication  │
├──────────────┼───────────┼───────────┼─────────────┼───────────┼──────────────┤
│ postgres     │ True      │ True      │ True        │ True      │ True         │
│ myapp_user   │ False     │ True      │ False       │ True      │ True         │
└──────────────┴───────────┴───────────┴─────────────┴───────────┴──────────────┘
```

#### `show connections`

Display active database connections with client information.

```bash
psqlc show connections
```

#### `show indexes`

Display indexes in database or specific table.

```bash
# Show all indexes in database
psqlc show indexes

# Show indexes for specific table
psqlc show indexes -d mydb -t users
```

**Options:**
- `-d, --database` - Database name (auto-detect if not provided)
- `-t, --table` - Table name (optional, shows all if not provided)

#### `show size`

Display size information for databases or tables.

```bash
# Show all database sizes
psqlc show size

# Show table sizes in a database
psqlc show size -d mydb

# Show size of specific table
psqlc show size -d mydb -t users
```

**Options:**
- `-d, --database` - Database name (auto-detect if not provided)
- `-t, --table` - Table name (optional, shows all tables if not provided)

**Example Output:**
```
📊 Size of table 'users':
   Total Size:   15 MB
   Table Size:   12 MB
   Indexes Size: 3 MB
```

### CREATE Command

Create a new PostgreSQL user and database with proper privileges.

```bash
# Method 1: Direct arguments
psqlc create username password dbname -U postgres

# Method 2: Named arguments
psqlc create -u username -p password -d dbname -U postgres

# Method 3: Auto-detect from settings.py
psqlc create -U postgres

# Method 4: From Django settings file
psqlc create /path/to/settings.py -U postgres
```

**Options:**
- `CONFIG` - Positional arguments: `NEW_USERNAME NEW_PASSWORD NEW_DB`
- `-u, --username` - New PostgreSQL username
- `-p, --password` - Password for new user
- `-d, --database` - Database name to create

**Features:**
- Automatically creates user with LOGIN, CREATEDB, REPLICATION, BYPASSRLS privileges
- Checks for existing database and prompts for confirmation before dropping
- Supports Django settings.py auto-detection

### DESCRIBE Command

Show detailed table structure including columns, data types, and constraints.

```bash
# Auto-detect database
psqlc describe -t users

# Specify database
psqlc describe -d mydb -t users
```

**Options:**
- `-d, --database` - Database name (auto-detect if not provided)
- `-t, --table` - Table name (required)

**Output:**
```
┌──────────────┬──────────────┬────────────┬──────────┬─────────────┐
│ Column       │ Type         │ Max Length │ Nullable │ Default     │
├──────────────┼──────────────┼────────────┼──────────┼─────────────┤
│ id           │ integer      │ -          │ NO       │ nextval()   │
│ username     │ varchar      │ 150        │ NO       │ -           │
│ email        │ varchar      │ 255        │ YES      │ -           │
│ created_at   │ timestamp    │ -          │ NO       │ now()       │
└──────────────┴──────────────┴────────────┴──────────┴─────────────┘
```

### QUERY Command

Execute custom SQL queries with safety features.

```bash
# Basic query
psqlc query -d mydb -q "SELECT * FROM users LIMIT 10"

# Read-only mode (prevents destructive operations)
psqlc query -d mydb -q "SELECT * FROM users" --readonly

# Limit rows displayed
psqlc query -d mydb -q "SELECT * FROM logs" --limit 50
```

**Options:**
- `-d, --database` - Database name (auto-detect if not provided)
- `-q, --query` - SQL query to execute (required)
- `--readonly` - Prevent destructive operations (blocks DROP, DELETE, TRUNCATE, ALTER, CREATE, INSERT, UPDATE)
- `--limit` - Limit number of rows displayed (default: 100)

**Safety Features:**
- Read-only mode blocks all destructive SQL commands
- Automatic transaction rollback on errors
- Row limit prevents memory issues with large result sets

### BACKUP Command

Generate backup command for a database using pg_dump.

```bash
# Auto-detect database
psqlc backup

# Specify database
psqlc backup -d mydb
```

**Options:**
- `-d, --database` - Database name to backup (auto-detect if not provided)

**Note:** This command generates the pg_dump command for you to run manually. Direct backup execution requires pg_dump to be installed and accessible in your PATH.

### DROP Commands

Safely drop databases or users with confirmation prompts.

#### `drop database`

Drop a database with safety confirmation.

```bash
# Auto-detect database
psqlc drop database

# Specify database
psqlc drop database -d mydb
```

**Options:**
- `-d, --database` - Database name to drop (auto-detect if not provided)

**Safety Features:**
- Requires typing the exact database name for confirmation
- Automatically terminates all active connections before dropping
- Cannot be undone - use with caution!

#### `drop user`

Drop a PostgreSQL user/role with safety confirmation.

```bash
psqlc drop user -u username
```

**Options:**
- `-u, --username` - Username to drop (required)

**Safety Features:**
- Requires typing the exact username for confirmation
- Cannot be undone - use with caution!

## 🔧 Django Settings.py Auto-detection

The tool automatically detects and parses Django `settings.py` files to extract PostgreSQL configuration. It searches:

1. Current working directory
2. Recursively down to 5 levels deep
3. Explicit paths provided as arguments

### Supported Settings Format

```python
# settings.py
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
```

### Auto-detection Priority

1. **Command-line arguments** (highest priority)
2. **Django settings.py** (if no CLI args provided)
3. **Interactive prompt** (for passwords only)

### Manual Settings Path

```bash
# Specify settings.py file
psqlc create /path/to/settings.py

# Specify directory containing settings.py
psqlc create /path/to/project/
```

## 💡 Examples

### Example 1: Complete Database Setup

```bash
# Create user and database from Django settings
psqlc create -U postgres

# Verify creation
psqlc show dbs
psqlc show users

# Check table structure
psqlc show tables
psqlc describe -t auth_user
```

### Example 2: Database Inspection

```bash
# Check database sizes
psqlc show size

# Check specific database details
psqlc show size -d mydb
psqlc show tables -d mydb
psqlc show indexes -d mydb

# Monitor connections
psqlc show connections
```

### Example 3: Safe Query Execution

```bash
# Read-only query (safe)
psqlc query -q "SELECT COUNT(*) FROM users" --readonly

# Regular query with limit
psqlc query -q "SELECT * FROM logs ORDER BY created_at DESC" --limit 20

# Complex query
psqlc query -q "
SELECT u.username, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.username
ORDER BY order_count DESC
" --readonly
```

### Example 4: Database Maintenance

```bash
# Backup database
psqlc backup -d production_db

# Check sizes before cleanup
psqlc show size -d production_db

# Drop old test database
psqlc drop database -d old_test_db

# Drop old user
psqlc drop user -u old_test_user
```

## 🔐 Security Best Practices

1. **Never hardcode passwords** - Use environment variables or settings files
2. **Use read-only mode** for SELECT queries in production
3. **Always confirm** before dropping databases or users
4. **Limit query results** to prevent memory issues
5. **Use connection timeouts** (built-in: 10 seconds)
6. **Regular backups** before major operations

## 🐛 Troubleshooting

### Enable Debug Mode

```bash
psqlc --debug show dbs
```

Debug mode shows:
- Settings.py detection attempts
- Connection details
- Detailed error messages

### Common Issues

#### "Connection failed"
- Check hostname, port, username, and password
- Verify PostgreSQL server is running
- Check firewall settings

#### "Settings.py not found"
- Ensure settings.py exists in current directory or subdirectories
- Try specifying the path explicitly
- Use `--debug` to see search paths

#### "Permission denied"
- Verify user has sufficient privileges
- Some operations require superuser access
- Check PostgreSQL user permissions

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug output | `0` |
| `TRACEBACK` | Show full tracebacks on errors | `0` |

Set environment variables:

```bash
# Linux/Mac
export DEBUG=1
psqlc show dbs

# Windows
set DEBUG=1
psqlc show dbs
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)
 
[Support me on Patreon](https://www.patreon.com/cumulus13)

## 🙏 Acknowledgments

- Built with [psycopg2](https://www.psycopg.org/) for PostgreSQL connectivity
- Styled with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Argument parsing with [licface](https://github.com/cumulus13/licface) for custom help formatting

## 📞 Support

For issues, questions, or contributions, please visit the project repository or contact the author.

---

**Note:** This tool is designed for PostgreSQL database management. Always test commands in a development environment before using in production.