#!/usr/bin/env python3
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-10-14
# Description: Production-ready PostgreSQL management CLI tool with asyncpg
# License: MIT

import sys
import os
import asyncio
from typing import Optional, Dict, Any
try:
    from richcolorlog import setup_logging
    logger = setup_logging()
except:
    import logging
    logger = logging.getLogger()

os.environ.update({'NO_LOGGING':'1'})

HOST = "127.0.0.1"
DEFAULT_PORT = 5432
_settings_cache = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_exception():
    from rich.console import Console
    console = Console()
    console.print_exception()

def rich_print(msg: str, color: str = "#FFFFFF", bgcolor: str = None, bold: bool = False, end: str = "\n"):
    """Print colored text using Rich"""
    from rich.console import Console
    from rich.style import Style
    from rich.text import Text
    
    console = Console()
    style_kwargs = {"color": color, "bold": bold}
    if bgcolor:
        style_kwargs["bgcolor"] = bgcolor
    
    console.print(Text(msg, style=Style(**style_kwargs)), end=end)


def load_settings_from_path(path: str):
    """Dynamically import a settings.py file"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("settings_module", path)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)
    return settings


def find_settings_recursive(start_path: str = None, max_depth: int = 5, filename: str = 'settings.py') -> Optional[str]:
    """Recursively search for settings file"""
    if start_path is None:
        start_path = os.getcwd()
    
    start_path = str(start_path)
    
    def search_directory(path: str, current_depth: int = 0) -> Optional[str]:
        if current_depth > max_depth:
            return None
        
        settings_path = os.path.join(path, filename)
        if os.path.isfile(settings_path):
            return settings_path
        
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if (os.path.isdir(item_path) and 
                    item not in ['node_modules', 'venv', '__pycache__'] and 
                    '-env' not in item):
                    result = search_directory(item_path, current_depth + 1)
                    if result:
                        return result
        except (PermissionError, OSError):
            pass
        
        return None
    
    return search_directory(start_path)


def parse_django_settings(settings_path: str = None) -> Optional[Dict[str, Any]]:
    """Parse Django settings.py or config files for database configuration"""
    global _settings_cache
    

    if _settings_cache is not None:
        return _settings_cache
    logger.debug(f"settings_path: {settings_path}")
    try:
        if settings_path is None:
            current_settings = os.path.join(os.getcwd(), "settings.py")
            if os.path.isfile(current_settings):
                settings_path = current_settings
            else:
                settings_path = find_settings_recursive()
        
        logger.debug(f"settings_path: {settings_path}")
        if settings_path: logger.info(f"os.path.isfile(settings_path): {os.path.isfile(settings_path)}")

        if not settings_path or not os.path.isfile(settings_path):
            for cf in [".env", ".json", ".yaml"]:
                settings_path = find_settings_recursive(filename=cf)
                logger.notice(f"settings_path: {settings_path}")
                if settings_path:
                    break
        
        if not settings_path or not os.path.isfile(settings_path):
            return None
        # print(f"settings_path: {settings_path}")
        # Parse settings.py

        final_path = settings_path
        logger.emergency(f"final_path: {final_path}")
        logger.emergency(f"final_path is file: {os.path.isfile(final_path)}")

        logger.warning(f"CHECK [1]: {final_path.endswith('settings.py') or 'settings.py' in final_path}")
        if final_path.endswith('settings.py') or 'settings.py' in final_path:
            logger.alert(f"processsing 'settings.py' in final_path ...")
            settings = load_settings_from_path(final_path)
            logger.info(f"settings: {settings}")
            databases_obj = getattr(settings, "DATABASES", None)
            logger.info(f"databases_obj: {databases_obj}")
            
            engine = None

            if databases_obj:
                for db_key, cfg in databases_obj.items():
                    if cfg.get("ENGINE") == "django.db.backends.postgresql" or cfg.get("ENGINE", '').lower() in ["postgresql", 'postgres', 'postgre'] or cfg.get("ENGINE") == ".postgresql":
                        engine = cfg.get("ENGINE")
                        rich_print(f"📄 Found settings at: {final_path}", color="#00CED1")
                        _settings_cache = {
                            'username': cfg.get("USER") or cfg.get("USERNAME") or cfg.get("user") or cfg.get("username"),
                            'password': cfg.get("PASSWORD") or cfg.get("PASS") or cfg.get("password") or cfg.get("pass"),
                            'database': cfg.get("NAME") or cfg.get("DB") or cfg.get("DB_NAME") or cfg.get("DBNAME") or cfg.get("name") or cfg.get("db") or cfg.get("db_name") or cfg.get("dbname"),
                            'host': cfg.get("HOST") or cfg.get("HOSTNAME") or cfg.get("SERVER") or cfg.get("host") or cfg.get("hostname") or cfg.get("server"),
                            'port': cfg.get("PORT") or cfg.get("port")
                        }
                        # print(f"_settings_cache: {_settings_cache}")
                        logger.notice(f"[{final_path}] _settings_cache: {_settings_cache}")
                        return _settings_cache
            if engine != "django.db.backends.postgresql":
                from rich.console import Console
                console = Console()
    
                console.print(f"❌ [bold #FFFF00]`settings.py` found but engine is[/] [bold #00FFFF]'{engine}'[/]")
        
        # Parse .env, .json, .yaml
        else:
            logger.debug(f"processing '{final_path}' ...")
            from envdot import load_env
            cfg = load_env(final_path)
            
            for key in ['engine', 'ENGINE', 'TYPE', 'type']:
                if cfg.get(key, '').lower() in ["django.db.backends.postgresql", "postgresql", "psql", "postgres", "postgre"] or cfg.get("POSTGRESQL_PORT") or cfg.get("postgresql_port") or cfg.get("POSTGRES_PORT") or cfg.get("postgres_port") or cfg.get("POSTGRE_PORT") or cfg.get("postgre_port"):
                    rich_print(f"📄 Found config at: {final_path}", color="#00CED1")
                    engine = cfg.get("ENGINE")
                    rich_print(f"📄 Found settings at: {final_path}", color="#00CED1")
                    _settings_cache = {
                        'username': cfg.get("POSTGRESQL_USERNAME") or \
                                    cfg.get("POSTGRESQL_USER") or \
                                    cfg.get("POSTGRES_USERNAME") or \
                                    cfg.get("POSTGRES_USER") or \
                                    cfg.get("POSTGRE_USERNAME") or \
                                    cfg.get("POSTGRE_USER") or \
                                    
                                    cfg.get("postgresql_username") or \
                                    cfg.get("postgresql_user") or \
                                    cfg.get("postgres_username") or \
                                    cfg.get("postgres_user") or \
                                    cfg.get("postgre_username") or \
                                    cfg.get("postgre_user") or \
                                    
                                    cfg.get("USER") or \
                                    cfg.get("USERNAME") or \
                                    cfg.get("user") or \
                                    cfg.get("username"),
                        'password': cfg.get("POSTGRESQL_PASSWORD") or \
                                    cfg.get("POSTGRESQL_PASS") or \
                                    cfg.get("POSTGRES_PASSWORD") or \
                                    cfg.get("POSTGRES_PASS") or \
                                    cfg.get("POSTGRE_PASSWORD") or \
                                    cfg.get("POSTGRE_PASS") or \
                                    
                                    cfg.get("postgresql_password") or \
                                    cfg.get("postgresql_pass") or \
                                    cfg.get("postgres_password") or \
                                    cfg.get("postgres_pass") or \
                                    cfg.get("postgre_password") or \
                                    cfg.get("postgre_pass") or \
                                    
                                    cfg.get("PASSWORD") or \
                                    cfg.get("PASS") or \
                                    cfg.get("password") or \
                                    cfg.get("pass"),
                        'database': cfg.get("POSTGRESQL_DB_NAME") or \
                                    cfg.get("POSTGRESQL_DBNAME") or \
                                    cfg.get("POSTGRESQL_DB") or \
                                    cfg.get("POSTGRESQL_NAME") or \
                                    cfg.get("POSTGRES_DB_NAME") or \
                                    cfg.get("POSTGRES_DBNAME") or \
                                    cfg.get("POSTGRES_DB") or \
                                    cfg.get("POSTGRES_NAME") or \
                                    cfg.get("POSTGRE_DB_NAME") or \
                                    cfg.get("POSTGRE_DBNAME") or \
                                    cfg.get("POSTGRE_DB") or \
                                    cfg.get("POSTGRE_NAME") or \

                                    cfg.get("postgresql_db_name") or \
                                    cfg.get("postgresql_dbname") or \
                                    cfg.get("postgresql_db") or \
                                    cfg.get("postgresql_name") or \
                                    cfg.get("postgres_db_name") or \
                                    cfg.get("postgres_dbname") or \
                                    cfg.get("postgres_db") or \
                                    cfg.get("postgres_name") or \
                                    cfg.get("postgre_db_name") or \
                                    cfg.get("postgre_dbname") or \
                                    cfg.get("postgre_db") or \
                                    cfg.get("postgre_name") or \

                                    cfg.get("NAME") or \
                                    cfg.get("DB") or \
                                    cfg.get("DB_NAME") or \
                                    cfg.get("DBNAME") or \
                                    cfg.get("name") or \
                                    cfg.get("db") or \
                                    cfg.get("db_name") or \
                                    cfg.get("dbname"),
                        'host': cfg.get("POSTGRESQL_HOSTNAME") or \
                                cfg.get("POSTGRESQL_HOST") or \
                                cfg.get("POSTGRES_HOSTNAME") or \
                                cfg.get("POSTGRES_HOST") or \
                                cfg.get("POSTGRE_HOSTNAME") or \
                                cfg.get("POSTGRE_HOST") or \

                                cfg.get("postgresql_hostname") or \
                                cfg.get("postgresql_host") or \
                                cfg.get("postgres_hostname") or \
                                cfg.get("postgres_host") or \
                                cfg.get("postgre_hostname") or \
                                cfg.get("postgre_host") or \
                                
                                cfg.get("SERVER") or \
                                cfg.get("host") or \
                                cfg.get("hostname") or \
                                cfg.get("server"),
                        'port': cfg.get("POSTGRESQL_PORT") or \
                                cfg.get("POSTGRES_PORT") or \
                                cfg.get("POSTGRE_PORT") or \
                                
                                cfg.get("postgresql_port") or \
                                cfg.get("postgres_port") or \
                                cfg.get("postgre_port") or \

                                cfg.get("PORT") or \
                                cfg.get("port")
                    }
                    # print(f"_settings_cache: {_settings_cache}")
                    logger.notice(f"[{final_path}] _settings_cache: {_settings_cache}")
                    return _settings_cache
    
    except Exception as e:
        #if os.getenv("DEBUG", "0") == "1":
            #rich_print(f"⚠️ Debug - Error reading settings: {e}", color="#FFFF00")
        logger.error(f"⚠️ Debug - Error reading settings: {e}")
        if str(os.getenv('TRACEBACK', '0')).lower() in ['1', 'true', 'yes']:
            import traceback
            logger.error(traceback.format_exc())
    
    return None


def get_version() -> str:
    """Get version from __version__.py file"""
    from pathlib import Path
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except:
        pass
    return "2.0"


# ============================================================================
# DATABASE CONNECTION
# ============================================================================

async def get_connection(host: str, port: int, user: str, password: str, 
                        database: str = "postgres", auto_settings: bool = True, settings_path = None):
    """Create async database connection"""
    import asyncpg
    
    if auto_settings:
        db_config = parse_django_settings()
        # print(f"db_config: {db_config}")
        if db_config:
            host = db_config.get('host') or host or os.getenv("HOST")
            port = db_config.get('port') or port or os.getenv("PORT")
            user = db_config.get('username') or user or os.getenv("USER")
            password = db_config.get('password') or password or os.getenv("PASSWORD")
            if db_config.get('database'): database = db_config.get('database')
            database = database or os.getenv('DATABASE') or os.getenv('DB_NAME') or os.getenv('DB')
    else:
        for cf in [".env", ".json", ".yaml"]:
            settings_path = find_settings_recursive(filename=cf)
            if settings_path:
                break
        
        if not settings_path or not os.path.isfile(settings_path):
            rich_print(f'❌ env file (".env", ".json", ".yaml") not Found !', color='bold red')
            return None

        from envdot import load_env
        cfg = load_env(settings_path)
        
        for key in ['engine', 'ENGINE', 'TYPE', 'type']:
            if cfg.get(key) in ["django.db.backends.postgresql", "postgresql", "psql"]:
                rich_print(f"📄 Found config at: {settings_path}", color="#00CED1")
                username = (cfg.get("USER") or cfg.get("user") or cfg.get("username") or cfg.get("USERNAME"))
                password = (cfg.get("PASSWORD") or cfg.get("password") or cfg.get("pass") or cfg.get("PASS"))
                database = (cfg.get("NAME") or cfg.get("name") or cfg.get("db") or cfg.get("DB") or cfg.get("dbname") or cfg.get("DBNAME") or cfg.get("db_name") or cfg.get("DB_NAME"))
                host = cfg.get("HOST") or cfg.get("host") or cfg.get("hostname")
                port = cfg.get("PORT") or cfg.get("port")

    host = os.getenv('HOST') or host
    port = os.getenv('PORT') or port
    user = os.getenv('USER') or user
    password = os.getenv('PASSWORD') or password
    database = os.getenv('DATABASE') or os.getenv('DB_NAME') or os.getenv('DB') or database

    rich_print(f"🔍 Using host={host}, user={user}, db={database}, passwd={'*'*len(password)}", color="#00CED1")
    
    try:
        return await asyncpg.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port,
            timeout=10
        )
    except Exception as e:
        rich_print(f"❌ Connection failed: {e}", color="#FF4500", bold=True)
        sys.exit(1)


def get_db_config_or_args(args):
    """Get database config from settings or args"""
    db_config = parse_django_settings()
    # print(f"db_config: {db_config}")
    if db_config:
        return {
            'host': db_config.get('host') or args.hostname,
            'port': db_config.get('port') or args.port,
            'user': db_config.get('username') or args.user,
            'password': args.passwd or  db_config.get('password')
        }
    else:
        return {
            'host': args.hostname,
            'port': args.port,
            'user': args.user,
            'password': args.passwd
        }


# ============================================================================
# SHOW COMMANDS
# ============================================================================

async def show_databases(args):
    """List all databases"""
    from rich.console import Console
    from rich.table import Table
    
    config = get_db_config_or_args(args)
    conn = await get_connection(**config, auto_settings=False)
    
    try:
        results = await conn.fetch("""
            SELECT 
                datname AS database,
                pg_size_pretty(pg_database_size(datname)) AS size,
                pg_encoding_to_char(encoding) AS encoding,
                datcollate AS collation
            FROM pg_database
            WHERE datistemplate = false
            ORDER BY datname;
        """)
        
        if not results:
            rich_print("📭 No databases found", color="#FFFF00")
            return
        
        table = Table(title="PostgreSQL Databases", show_header=True, header_style="bold magenta")
        table.add_column("Database", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Encoding", style="yellow")
        table.add_column("Collation", style="blue")
        
        for row in results:
            table.add_row(row['database'], row['size'], row['encoding'], row['collation'])
        
        Console().print(table)
    
    except Exception as e:
        rich_print(f"❌ Error: {e}", color="#FF4500", bold=True)
    finally:
        await conn.close()


async def show_tables(args):
    """List all tables in a database"""
    from rich.console import Console
    from rich.table import Table
    
    if not args.database:
        db_config = parse_django_settings()
        if db_config and db_config.get('database'):
            args.database = db_config.get('database')
            rich_print(f"📄 Using database: {args.database}", color="#00CED1")
        else:
            rich_print("❌ Database name required. Use -d/--database", color="#FF4500", bold=True)
            return
    
    config = get_db_config_or_args(args)
    conn = await get_connection(**config, database=args.database, auto_settings=False)
    
    try:
        results = await conn.fetch("""
            SELECT 
                schemaname AS schema,
                tablename AS table,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                (SELECT COUNT(*) FROM information_schema.columns 
                 WHERE table_schema = schemaname AND table_name = tablename) AS columns
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schemaname, tablename;
        """)
        
        if not results:
            rich_print(f"📭 No tables found in '{args.database}'", color="#FFFF00")
            return
        
        table = Table(title=f"Tables in '{args.database}'", show_header=True, header_style="bold magenta")
        table.add_column("Schema", style="cyan")
        table.add_column("Table", style="green")
        table.add_column("Size", style="yellow")
        table.add_column("Columns", style="blue")
        
        for row in results:
            table.add_row(row['schema'], row['table'], row['size'], str(row['columns']))
        
        Console().print(table)
    
    except Exception as e:
        rich_print(f"❌ Error: {e}", color="#FF4500", bold=True)
    finally:
        await conn.close()


async def show_users(args):
    """List all database users/roles"""
    from rich.console import Console
    from rich.table import Table
    
    config = get_db_config_or_args(args)
    conn = await get_connection(**config, auto_settings=False)
    
    try:
        results = await conn.fetch("""
            SELECT 
                rolname AS username,
                rolsuper AS superuser,
                rolcreatedb AS create_db,
                rolcreaterole AS create_role,
                rolcanlogin AS can_login,
                rolreplication AS replication
            FROM pg_roles
            WHERE rolname NOT LIKE 'pg_%'
            ORDER BY rolname;
        """)
        
        table = Table(title="PostgreSQL Users", show_header=True, header_style="bold magenta")
        table.add_column("Username", style="cyan")
        table.add_column("Superuser", style="red")
        table.add_column("Create DB", style="green")
        table.add_column("Create Role", style="yellow")
        table.add_column("Can Login", style="blue")
        table.add_column("Replication", style="magenta")
        
        for row in results:
            table.add_row(
                row['username'], str(row['superuser']), str(row['create_db']),
                str(row['create_role']), str(row['can_login']), str(row['replication'])
            )
        
        Console().print(table)
    
    except Exception as e:
        rich_print(f"❌ Error: {e}", color="#FF4500", bold=True)
    finally:
        await conn.close()


async def show_connections(args):
    """Show active database connections"""
    from rich.console import Console
    from rich.table import Table
    
    config = get_db_config_or_args(args)
    conn = await get_connection(**config, auto_settings=False)
    
    try:
        results = await conn.fetch("""
            SELECT 
                datname AS database,
                usename AS username,
                client_addr AS client,
                state,
                query_start,
                state_change
            FROM pg_stat_activity
            WHERE datname IS NOT NULL
            ORDER BY query_start DESC;
        """)
        
        if not results:
            rich_print("📭 No active connections", color="#FFFF00")
            return
        
        table = Table(title="Active Connections", show_header=True, header_style="bold magenta")
        table.add_column("Database", style="cyan")
        table.add_column("User", style="green")
        table.add_column("Client", style="yellow")
        table.add_column("State", style="blue")
        table.add_column("Query Start", style="magenta")
        table.add_column("State Change", style="red")
        
        for row in results:
            table.add_row(
                str(row['database'] or "-"), str(row['username'] or "-"),
                str(row['client'] or "-"), str(row['state'] or "-"),
                str(row['query_start'] or "-"), str(row['state_change'] or "-")
            )
        
        Console().print(table)
    
    except Exception as e:
        rich_print(f"❌ Error: {e}", color="#FF4500", bold=True)
    finally:
        await conn.close()


async def show_indexes(args):
    """Show indexes in a table or database"""
    from rich.console import Console
    from rich.table import Table
    
    if not args.database:
        db_config = parse_django_settings()
        if db_config and db_config.get('database'):
            args.database = db_config.get('database')
            rich_print(f"📄 Using database: {args.database}", color="#00CED1")
        else:
            rich_print("❌ Database name required. Use -d/--database", color="#FF4500", bold=True)
            return
    
    config = get_db_config_or_args(args)
    conn = await get_connection(**config, database=args.database, auto_settings=False)
    
    try:
        if args.table:
            results = await conn.fetch("""
                SELECT indexname AS index_name, indexdef AS definition
                FROM pg_indexes
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                AND tablename = $1
                ORDER BY indexname;
            """, args.table)
            title = f"Indexes in table '{args.table}'"
        else:
            results = await conn.fetch("""
                SELECT schemaname AS schema, tablename AS table,
                       indexname AS index_name, indexdef AS definition
                FROM pg_indexes
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY schemaname, tablename, indexname;
            """)
            title = f"Indexes in database '{args.database}'"
        
        if not results:
            rich_print(f"📭 No indexes found", color="#FFFF00")
            return
        
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        if args.table:
            table.add_column("Index Name", style="cyan")
            table.add_column("Definition", style="green")
            for row in results:
                table.add_row(row['index_name'], row['definition'])
        else:
            table.add_column("Schema", style="cyan")
            table.add_column("Table", style="green")
            table.add_column("Index Name", style="yellow")
            table.add_column("Definition", style="blue")
            for row in results:
                table.add_row(row['schema'], row['table'], row['index_name'], row['definition'])
        
        Console().print(table)
    
    except Exception as e:
        rich_print(f"❌ Error: {e}", color="#FF4500", bold=True)
    finally:
        await conn.close()


async def show_size(args):
    """Show database or table sizes"""
    from rich.console import Console
    from rich.table import Table
    
    if not args.database:
        db_config = parse_django_settings()
        if db_config and db_config.get('database'):
            args.database = db_config.get('database')
            rich_print(f"📄 Using database: {args.database}", color="#00CED1")
        else:
            # Show all database sizes
            config = get_db_config_or_args(args)
            conn = await get_connection(**config, auto_settings=False)
            
            try:
                results = await conn.fetch("""
                    SELECT datname AS database,
                           pg_size_pretty(pg_database_size(datname)) AS size,
                           pg_database_size(datname) AS size_bytes
                    FROM pg_database
                    WHERE datistemplate = false
                    ORDER BY pg_database_size(datname) DESC;
                """)
                
                table = Table(title="Database Sizes", show_header=True, header_style="bold magenta")
                table.add_column("Database", style="cyan")
                table.add_column("Size", style="green")
                
                total_size = sum(row['size_bytes'] for row in results)
                for row in results:
                    table.add_row(row['database'], row['size'])
                
                Console().print(table)
                rich_print(f"\n📊 Total Size: {total_size / (1024**3):.2f} GB", color="#00CED1", bold=True)
            
            except Exception as e:
                rich_print(f"❌ Error: {e}", color="#FF4500", bold=True)
            finally:
                await conn.close()
            return
    
    config = get_db_config_or_args(args)
    conn = await get_connection(**config, database=args.database, auto_settings=False)
    
    try:
        if args.table:
            result = await conn.fetchrow("""
                SELECT pg_size_pretty(pg_total_relation_size($1)) AS total_size,
                       pg_size_pretty(pg_relation_size($1)) AS table_size,
                       pg_size_pretty(pg_total_relation_size($1) - pg_relation_size($1)) AS indexes_size
            """, args.table)
            
            if result:
                rich_print(f"\n📊 Size of table '{args.table}':", color="#00CED1", bold=True)
                rich_print(f"   Total Size:   {result['total_size']}", color="#00FF7F")
                rich_print(f"   Table Size:   {result['table_size']}", color="#FFFF00")
                rich_print(f"   Indexes Size: {result['indexes_size']}", color="#FF69B4")
            else:
                rich_print(f"❌ Table '{args.table}' not found", color="#FF4500", bold=True)
        else:
            results = await conn.fetch("""
                SELECT schemaname AS schema, tablename AS table,
                       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
                       pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
                FROM pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """)
            
            if not results:
                rich_print(f"📭 No tables found in '{args.database}'", color="#FFFF00")
                return
            
            table = Table(title=f"Table Sizes in '{args.database}'", show_header=True, header_style="bold magenta")
            table.add_column("Schema", style="cyan")
            table.add_column("Table", style="green")
            table.add_column("Total Size", style="yellow")
            
            total_size = sum(row['size_bytes'] for row in results)
            for row in results:
                table.add_row(row['schema'], row['table'], row['total_size'])
            
            Console().print(table)
            rich_print(f"\n📊 Total Size: {total_size / (1024**3):.2f} GB", color="#00CED1", bold=True)
    
    except Exception as e:
        rich_print(f"❌ Error: {e}", color="#FF4500", bold=True)
    finally:
        await conn.close()


# ============================================================================
# DESCRIBE & QUERY COMMANDS
# ============================================================================

async def describe_table(args):
    """Show table structure"""
    from rich.console import Console
    from rich.table import Table
    
    if not args.database:
        db_config = parse_django_settings()
        if db_config and db_config.get('database'):
            args.database = db_config.get('database')
            rich_print(f"📄 Using database: {args.database}", color="#00CED1")
        else:
            rich_print("❌ Database name required. Use -d/--database", color="#FF4500", bold=True)
            return
    
    if not args.table:
        rich_print("❌ Table name required. Use -t/--table", color="#FF4500", bold=True)
        return
    
    config = get_db_config_or_args(args)
    conn = await get_connection(**config, database=args.database, auto_settings=False)
    
    try:
        results = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length,
                   is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = $1
            ORDER BY ordinal_position;
        """, args.table)
        
        if not results:
            rich_print(f"❌ Table '{args.table}' not found", color="#FF4500", bold=True)
            return
        
        table = Table(title=f"Structure of '{args.table}'", show_header=True, header_style="bold magenta")
        table.add_column("Column", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Max Length", style="yellow")
        table.add_column("Nullable", style="blue")
        table.add_column("Default", style="magenta")
        
        for row in results:
            table.add_row(
                row['column_name'], row['data_type'],
                str(row['character_maximum_length']) if row['character_maximum_length'] else "-",
                row['is_nullable'],
                str(row['column_default']) if row['column_default'] else "-"
            )
        
        Console().print(table)
    
    except Exception as e:
        rich_print(f"❌ Error: {e}", color="#FF4500", bold=True)
    finally:
        await conn.close()


async def execute_query(args):
    """Execute a custom SQL query"""
    from rich.console import Console
    from rich.table import Table
    
    if not args.database:
        db_config = parse_django_settings()
        if db_config and db_config.get('database'):
            args.database = db_config.get('database')
            rich_print(f"📄 Using database: {args.database}", color="#00CED1")
        else:
            rich_print("❌ Database name required. Use -d/--database", color="#FF4500", bold=True)
            return
    
    if not args.query:
        rich_print("❌ Query required. Use -q/--query", color="#FF4500", bold=True)
        return
    
    if args.readonly:
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
        if any(keyword in args.query.upper() for keyword in dangerous_keywords):
            rich_print("❌ Destructive queries not allowed in read-only mode", color="#FF4500", bold=True)
            return
    
    config = get_db_config_or_args(args)
    conn = await get_connection(**config, database=args.database, auto_settings=False)
    
    try:
        if args.query.strip().upper().startswith('SELECT'):
            results = await conn.fetch(args.query)
            
            if not results:
                rich_print("✅ Query executed. No rows returned.", color="#00FF7F")
                return
            
            columns = list(results[0].keys())
            table = Table(title="Query Results", show_header=True, header_style="bold magenta")
            
            for col in columns:
                table.add_column(col, style="cyan")
            
            max_rows = getattr(args, 'limit', 100) or 100
            for row in results[:max_rows]:
                table.add_row(*[str(row[col]) if row[col] is not None else "NULL" for col in columns])
            
            Console().print(table)
            
            if len(results) > max_rows:
                rich_print(f"⚠️ Showing {max_rows} of {len(results)} rows", color="#FFFF00", bold=True)
        else:
            await conn.execute(args.query)
            rich_print("✅ Query executed successfully", color="#00FF7F", bold=True)
    
    except Exception as e:
        rich_print(f"❌ Query error: {e}", color="#FF4500", bold=True)
    finally:
        await conn.close()


# ============================================================================
# CREATE & DROP COMMANDS
# ============================================================================

async def create_user_db(args):
    """Create PostgreSQL user and database"""
    import asyncpg
    from pwinput import pwinput

    username = password = database = None
    PORT = args.port or DEFAULT_PORT
    HOST = args.hostname
    
    # Parse configuration
    if args.CONFIG and len(args.CONFIG) == 3:
        username, password, database = args.CONFIG
    elif not args.username and not args.password and not args.database:
        db_config = parse_django_settings()
        if db_config:
            username = db_config.get('username')
            password = db_config.get('password')
            database = db_config.get('database')
            HOST = db_config.get('host') or HOST
            PORT = db_config.get('port') or PORT
    elif args.CONFIG and len(args.CONFIG) == 1:
        if os.path.isfile(args.CONFIG[0]) and args.CONFIG[0].endswith("settings.py"):
            db_config = parse_django_settings(args.CONFIG[0])
        elif os.path.isdir(args.CONFIG[0]):
            settings_path = os.path.join(args.CONFIG[0], "settings.py")
            if os.path.isfile(settings_path):
                db_config = parse_django_settings(settings_path)
        
        if db_config:
            username = db_config.get('username')
            password = db_config.get('password')
            database = db_config.get('database')
            HOST = db_config.get('host') or HOST
            PORT = db_config.get('port') or PORT
    
    if not username or not password or not database:
        username = username or args.username
        password = password or args.password
        database = database or args.database
    
    if not all([username, password, database]):
        rich_print("❌ Missing required info (username, password, database)", color="#FF4500", bold=True)
        sys.exit(1)
    
    rich_print(f"🕵🏿 USERNAME: {username}", color="#00CED1", bold=True)
    rich_print(f"🔑 PASSWORD: {'*****' if password else ''}", color="#FFFF00", bold=True)
    rich_print(f"🧰 DATABASE: {database}", color="#00FF7F", bold=True)
    rich_print(f"👻 HOSTNAME: {HOST}", color="#FFFFFF")
    rich_print(f"🚢 PORT: {PORT}", color="#FFFFFF")
    
    async def start():
        logger.info(f"args.user: {args.user}")
        logger.info(f"args.password: {args.password}")
        logger.info(f"HOST: {HOST}")
        logger.info(f"PORT: {PORT}")

        conn = await asyncpg.connect(database="postgres", user=args.user, host=HOST, port=PORT, password=args.passwd)
        
        try:
            await conn.execute(f"CREATE USER {username} WITH PASSWORD '{password}'")
            rich_print(f"✅ User '{username}' created", color="#00FF7F", bold=True)
        except asyncpg.DuplicateObjectError:
            rich_print(f"⚠️ User '{username}' already exists", color="#FFFF00", bold=True)
        
        await conn.execute(f"ALTER USER {username} WITH LOGIN CREATEDB REPLICATION BYPASSRLS")
        rich_print(f"✅ User '{username}' updated with privileges", color="#00FF7F", bold=True)
        
        await conn.close()
        rich_print("🔒 Logged out from postgres superuser", color="#00CED1")

    # Create user
    try:
        await start()
    except asyncpg.InvalidPasswordError:
        rich_print("❌ Invalid PostgreSQL password", color="#FF4500", bold=True)
        pwinput(f"[{os.getpid()}]Password for {args.user}: ")
        return
    
    except Exception as e:
        if str(os.getenv('TRACEBACK', '0')).lower() in ['1', 'yes', 'true']:
            print_exception()
        else:
            rich_print(f"❌ Error (superuser connection): {e}", color="#FF4500", bold=True)
            while 1:
                args.password = pwinput(f"[{os.getpid()}]Password for {args.user} [q/x/quit/exit for exit]: ")
                if args.password:
                    if args.password in ['x', 'q', 'exit', 'quit']:
                        rich_print(f"❌ exit/quit without password user '{args.user}' nedded !", color="#FF4500", bold=True)
                        return
                    else:
                        break
        return
    
    # Create database
    try:
        conn = await asyncpg.connect(database="template1", user=username, password=password, host=HOST, port=PORT)
        
        result = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", database)
        if result:
            rich_print(f"⚠️ Database '{database}' already exists.", color="#FFFF00", bold=True)
            rich_print(f"❓ Drop and recreate '{database}'? [y/N]: ", color="#FFFF00", bold=True, end="")
            choice = input().strip().lower()
            
            if choice == "y":
                try:
                    await conn.execute(f"DROP DATABASE {database}")
                    rich_print(f"🗑️ Database '{database}' dropped", color="#FF4500", bold=True)
                    await conn.execute(f"CREATE DATABASE {database}")
                    rich_print(f"✅ Database '{database}' recreated", color="#00FF7F", bold=True)
                except Exception as e:
                    rich_print(f"❌ Error: {e}", color="#FF4500", bold=True)
            else:
                rich_print(f"⏭️ Skipping database creation", color="#FFFF00", bold=True)
        else:
            try:
                await conn.execute(f"CREATE DATABASE {database}")
                rich_print(f"✅ Database '{database}' created", color="#00FF7F", bold=True)
            except Exception as e:
                if "already exists" not in str(e):
                    raise
                rich_print(f"⚠️ Database '{database}' already exists", color="#FFFF00", bold=True)
        
        await conn.close()
        rich_print("🔒 Logged out from new user session", color="#00CED1")
    
    except Exception as e:
        if os.getenv("TRACEBACK", "0").lower() in ["1", "true", "yes"]:
            import traceback
            print(traceback.format_exc())
        else:
            rich_print(f"❌ Error (new user connection): {e}", color="#FF4500", bold=True)


async def drop_database(args):
    """Drop a database with confirmation"""
    import asyncpg
    
    if not args.database:
        db_config = parse_django_settings()
        if db_config and db_config.get('database'):
            args.database = db_config.get('database')
            rich_print(f"📄 Using database: {args.database}", color="#00CED1")
        else:
            rich_print("❌ Database name required. Use -d/--database", color="#FF4500", bold=True)
            return
    
    rich_print(f"⚠️  WARNING: You are about to DROP database '{args.database}'", color="#FF4500", bold=True)
    rich_print(f"❓ Type the database name to confirm: ", color="#FFFF00", bold=True, end="")
    confirmation = input().strip()
    
    if confirmation != args.database:
        rich_print("❌ Database name mismatch. Aborted.", color="#FF4500", bold=True)
        return
    
    try:
        conn = await asyncpg.connect(
            database="postgres",
            user=args.user,
            host=args.hostname,
            port=args.port,
            password=args.passwd,
        )
        
        await conn.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = $1 AND pid <> pg_backend_pid()
        """, args.database)
        
        await conn.execute(f"DROP DATABASE IF EXISTS {args.database}")
        rich_print(f"✅ Database '{args.database}' dropped successfully", color="#00FF7F", bold=True)
        
        await conn.close()
    
    except Exception as e:
        rich_print(f"❌ Error dropping database: {e}", color="#FF4500", bold=True)


async def drop_user(args):
    """Drop a user/role with confirmation"""
    import asyncpg
    
    if not args.username:
        rich_print("❌ Username required. Use -u/--username", color="#FF4500", bold=True)
        return
    
    rich_print(f"⚠️  WARNING: You are about to DROP user '{args.username}'", color="#FF4500", bold=True)
    rich_print(f"❓ Type the username to confirm: ", color="#FFFF00", bold=True, end="")
    confirmation = input().strip()
    
    if confirmation != args.username:
        rich_print("❌ Username mismatch. Aborted.", color="#FF4500", bold=True)
        return
    
    try:
        conn = await asyncpg.connect(
            database="postgres",
            user=args.user,
            host=args.hostname,
            port=args.port,
            password=args.passwd,
        )
        
        await conn.execute(f"DROP USER IF EXISTS {args.username}")
        rich_print(f"✅ User '{args.username}' dropped successfully", color="#00FF7F", bold=True)
        
        await conn.close()
    
    except Exception as e:
        rich_print(f"❌ Error dropping user: {e}", color="#FF4500", bold=True)


# ============================================================================
# BACKUP COMMAND
# ============================================================================

def backup_database(args):
    """Generate backup command for database"""
    from datetime import datetime
    
    if not args.database:
        db_config = parse_django_settings()
        if db_config and db_config.get('database'):
            args.database = db_config.get('database')
            rich_print(f"📄 Using database: {args.database}", color="#00CED1")
        else:
            rich_print("❌ Database name required. Use -d/--database", color="#FF4500", bold=True)
            return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{args.database}_backup_{timestamp}.sql"
    
    rich_print(f"🗄️ Creating backup of '{args.database}'...", color="#00CED1", bold=True)
    
    cmd = f"pg_dump -h {args.hostname} -p {args.port} -U {args.user} -d {args.database} -F p -f {backup_file}"
    
    rich_print(f"💡 Run this command manually:", color="#FFFF00")
    rich_print(f"   {cmd}", color="#00FF7F")


# ============================================================================
# MAIN & ARGUMENT PARSER
# ============================================================================

def setup_argument_parser():
    """Setup and configure argument parser"""
    import argparse
    from licface import CustomRichHelpFormatter
    
    parser = argparse.ArgumentParser(
        description="Production-ready PostgreSQL management CLI tool with asyncpg",
        formatter_class=CustomRichHelpFormatter,
        prog='psqlc'
    )
    
    # Global options
    parser.add_argument("-H", "--hostname", default=HOST, help=f"PostgreSQL server address (default: {HOST})")
    parser.add_argument("-U", "--user", default="postgres", help="PostgreSQL superuser (default: postgres)")
    parser.add_argument("-P", "--passwd", help="PostgreSQL superuser password")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"PostgreSQL server port (default: {DEFAULT_PORT})")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument('-v', "--version", action="store_true", help="Show version")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # SHOW command
    show_parser = subparsers.add_parser('show', help='Show database information', formatter_class=CustomRichHelpFormatter)
    show_subparsers = show_parser.add_subparsers(dest='show_command', help='Show options')
    
    show_subparsers.add_parser('dbs', help='List all databases', formatter_class=CustomRichHelpFormatter)
    
    show_tables_parser = show_subparsers.add_parser('tables', help='List tables in database', formatter_class=CustomRichHelpFormatter)
    show_tables_parser.add_argument("-d", "--database", help="Database name (auto-detect if not provided)")
    show_tables_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    show_subparsers.add_parser('users', help='List all users/roles', formatter_class=CustomRichHelpFormatter)
    show_subparsers.add_parser('connections', help='Show active connections', formatter_class=CustomRichHelpFormatter)
    
    show_indexes_parser = show_subparsers.add_parser('indexes', help='Show indexes', formatter_class=CustomRichHelpFormatter)
    show_indexes_parser.add_argument("-d", "--database", help="Database name (auto-detect if not provided)")
    show_indexes_parser.add_argument("-t", "--table", help="Table name (optional)")
    show_indexes_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    show_size_parser = show_subparsers.add_parser('size', help='Show sizes', formatter_class=CustomRichHelpFormatter)
    show_size_parser.add_argument("-d", "--database", help="Database name (auto-detect if not provided)")
    show_size_parser.add_argument("-t", "--table", help="Table name (optional)")
    show_size_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # CREATE command
    create_parser = subparsers.add_parser('create', help='Create user and database', formatter_class=CustomRichHelpFormatter)
    create_parser.add_argument("CONFIG", nargs="*", help="Format: NEW_USERNAME NEW_PASSWORD NEW_DB")
    create_parser.add_argument("-u", "--username", help="New PostgreSQL username")
    create_parser.add_argument("-p", "--password", help="Password for new user")
    create_parser.add_argument("-d", "--database", help="Database name to create")
    create_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # DESCRIBE command
    desc_parser = subparsers.add_parser('describe', help='Show table structure', formatter_class=CustomRichHelpFormatter)
    desc_parser.add_argument("-d", "--database", help="Database name (auto-detect if not provided)")
    desc_parser.add_argument("-t", "--table", required=True, help="Table name")
    desc_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # QUERY command
    query_parser = subparsers.add_parser('query', help='Execute SQL query', formatter_class=CustomRichHelpFormatter)
    query_parser.add_argument("-d", "--database", help="Database name (auto-detect if not provided)")
    query_parser.add_argument("-q", "--query", required=True, help="SQL query to execute")
    query_parser.add_argument("--readonly", action="store_true", help="Prevent destructive operations")
    query_parser.add_argument("--limit", type=int, help="Limit rows displayed (default: 100)")
    query_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # BACKUP command
    backup_parser = subparsers.add_parser('backup', help='Backup database', formatter_class=CustomRichHelpFormatter)
    backup_parser.add_argument("-d", "--database", help="Database name (auto-detect if not provided)")
    backup_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # DROP command
    drop_parser = subparsers.add_parser('drop', help='Drop database or user', formatter_class=CustomRichHelpFormatter)
    drop_subparsers = drop_parser.add_subparsers(dest='drop_command', help='Drop options')
    
    drop_db_parser = drop_subparsers.add_parser('database', help='Drop a database', formatter_class=CustomRichHelpFormatter)
    drop_db_parser.add_argument("-d", "--database", help="Database name (auto-detect if not provided)")
    drop_db_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    drop_user_parser = drop_subparsers.add_parser('user', help='Drop a user/role', formatter_class=CustomRichHelpFormatter)
    drop_user_parser.add_argument("-u", "--username", required=True, help="Username to drop")
    drop_user_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    return parser


async def run_command(args, show_parser, drop_parser):
    """Route to appropriate command handler"""
    if args.command == 'create':
        await create_user_db(args)
    elif args.command == 'show':
        if args.show_command == 'dbs':
            await show_databases(args)
        elif args.show_command == 'tables':
            await show_tables(args)
        elif args.show_command == 'users':
            await show_users(args)
        elif args.show_command == 'connections':
            await show_connections(args)
        elif args.show_command == 'indexes':
            await show_indexes(args)
        elif args.show_command == 'size':
            await show_size(args)
        else:
            show_parser.print_help()
    elif args.command == 'describe':
        await describe_table(args)
    elif args.command == 'query':
        await execute_query(args)
    elif args.command == 'backup':
        backup_database(args)
    elif args.command == 'drop':
        if args.drop_command == 'database':
            await drop_database(args)
        elif args.drop_command == 'user':
            await drop_user(args)
        else:
            drop_parser.print_help()


def main():
    """Main entry point"""
    # import getpass
    from pwinput import pwinput
    from rich.console import Console
    import argparse

    # Early version check
    if '--version' in sys.argv or '-v' in sys.argv:
        Console().print(f"📦 [bold #FFFF00]Version:[/] [bold #00FFFF]{get_version()}[/]")
        sys.exit(0)
    
    parser = setup_argument_parser()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Set debug mode
    if hasattr(args, 'debug') and args.debug:
        os.environ["DEBUG"] = "1"
        os.environ['LOGGING'] = "1"
        os.environ.pop('NO_LOGGING')
    
    # Get password from settings or prompt
    if not args.passwd and args.command:
        db_config = parse_django_settings()
        logger.info(f"db_config = {db_config}")
        if db_config and db_config.get('password'):
            args.passwd = db_config.get('password')
            #if os.getenv("DEBUG", "0") == "1":
                #rich_print("🔐 Using password from settings", color="#00CED1")
            logger.warning("🔐 Using password from settings", color="#00CED1")
        else:
            args.passwd = os.getenv('PASSWORD') or pwinput(f"[{os.getpid()}]Password for {args.user}: ")
    
    # Get references to parsers for help display
    show_parser = None
    drop_parser = None
    for action in parser._subparsers._actions:
        if isinstance(action, argparse._SubParsersAction):
            show_parser = action.choices.get('show')
            drop_parser = action.choices.get('drop')
    
    # Run async command
    asyncio.run(run_command(args, show_parser, drop_parser))


if __name__ == "__main__":
    main()