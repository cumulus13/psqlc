#!/usr/bin/env python3
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-09-28 23:31:00.473179
# Description: Create PostgreSQL user and database.
# License: MIT

import argparse
import psycopg2
from psycopg2 import sql, errors
from licface import CustomRichHelpFormatter
import sys
import traceback
import os
import importlib
from rich.console import Console
from rich.style import Style
from rich.text import Text

HOST = "222.222.222.5"

console = Console()

def rich_print(msg: str, color: str = "#FFFFFF", bgcolor: str | None = None, bold: bool = False, end: str = "\n"):
    """Print text with hex color using Rich"""
    style_kwargs = {"color": color}
    if bgcolor:
        style_kwargs["bgcolor"] = bgcolor
    if bold:
        style_kwargs["bold"] = True
    style = Style(**style_kwargs)
    console.print(Text(msg, style=style), end=end)


def load_settings_from_path(path):
    """Dynamically import a settings.py file from any path"""
    spec = importlib.util.spec_from_file_location("settings_module", path)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)
    return settings

def main():
    parser = argparse.ArgumentParser(
        description="Create PostgreSQL user and database.",
        formatter_class=CustomRichHelpFormatter,
    )
    parser.add_argument("CONFIG", help="Format NEW_USERNAME NEW_PASSWORD NEW_DB", nargs="*")
    parser.add_argument("-u", "--username", help="New PostgreSQL username")
    parser.add_argument("-p", "--password", help="Password for new user")
    parser.add_argument("-d", "--database", help="Database name to create")
    parser.add_argument(
        "-H", "--hostname", help=f"Postgresql Server address/hostname/ip, default={HOST}", default=HOST
    )
    parser.add_argument("-U", "--user", help="Postgresql superuser, default='postgres'", default="postgres")
    parser.add_argument("-P", "--passwd", help="Postgresql superuser password")
    parser.add_argument("--port", help="Postgresql Server port, default: 5432", default=5432, type=int)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    PORT = args.port or 5432
    username = password = database = None

    # --- CASE 1: CONFIG direct args
    if args.CONFIG and len(args.CONFIG) == 3:
        username, password, database = args.CONFIG

    # --- CASE 2: Django settings.py di current dir
    elif os.path.isfile(os.path.join(os.getcwd(), "settings.py")):
        settings = importlib.import_module("settings")
        databases_obj = getattr(settings, "DATABASES", None)
        if databases_obj:
            for db_key, cfg in databases_obj.items():
                if cfg.get("ENGINE") == "django.db.backends.postgresql":
                    username = cfg.get("USER")
                    password = cfg.get("PASSWORD")
                    database = cfg.get("NAME")
                    PORT = cfg.get("PORT") or PORT

    # --- CASE 3: settings.py explicit file path
    elif args.CONFIG and os.path.isfile(args.CONFIG[0]) and args.CONFIG[0].endswith("settings.py"):
        settings = load_settings_from_path(args.CONFIG[0])
        databases_obj = getattr(settings, "DATABASES", None)
        if databases_obj:
            for db_key, cfg in databases_obj.items():
                if cfg.get("ENGINE") == "django.db.backends.postgresql":
                    username = cfg.get("USER")
                    password = cfg.get("PASSWORD")
                    database = cfg.get("NAME")
                    PORT = cfg.get("PORT") or PORT

    # --- CASE 4: folder with settings.py
    elif args.CONFIG and os.path.isdir(args.CONFIG[0]) and os.path.isfile(os.path.join(args.CONFIG[0], "settings.py")):
        settings_path = os.path.join(args.CONFIG[0], "settings.py")
        settings = load_settings_from_path(settings_path)
        databases_obj = getattr(settings, "DATABASES", None)
        if databases_obj:
            for db_key, cfg in databases_obj.items():
                if cfg.get("ENGINE") == "django.db.backends.postgresql":
                    username = cfg.get("USER")
                    password = cfg.get("PASSWORD")
                    database = cfg.get("NAME")
                    PORT = cfg.get("PORT") or PORT

    # --- CASE 5: Fallback manual args
    else:
        username = args.username
        password = args.password
        database = args.database

    if not all([username, password, database]):
        # print("❌ Missing required info (username, password, database)")
        rich_print("❌ Missing required info (username, password, database)", color="#FF4500", bold=True)
        sys.exit(1)
    # else:
    # print(f"🕵🏿USERNAME: {username}")
    rich_print(f"🕵🏿USERNAME: {username}", color="#00CED1", bold=True)
    # print(f"🔑 PASSWORD: {'*****' if password else ''}")
    rich_print(f"🔑 PASSWORD: {'*****' if password else ''}", color="#FFFF00", bold=True)
    # print(f"🧰 DATABASE: {database}")
    rich_print(f"🧰 DATABASE: {database}", color="#00FF7F", bold=True)
    # print(f"👻 HOSTNAME: {args.hostname}")
    rich_print(f"👻 HOSTNAME: {args.hostname}", color="#FFFFFF")
    # print(f"🚢 PORT: {PORT}")
    rich_print(f"🚢 PORT: {PORT}", color="#FFFFFF")

    # Step 1: connect as postgres superuser
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=args.user,
            host=args.hostname,
            port=PORT,
            password=args.passwd,
        )
        conn.autocommit = True
        cur = conn.cursor()

        # Step 2: create user
        try:
            cur.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(username)),
                [password],
            )
            # print(f"✅ User '{username}' created")
            rich_print(f"✅ User '{username}' created", color="#00FF7F", bold=True)
        except errors.DuplicateObject:
            # print(f"⚠️ User '{username}' already exists, skipping")
            rich_print(f"⚠️ User '{username}' already exists, skipping", color="#FFFF00", bold=True)

        # Step 3: alter user privileges
        cur.execute(
            sql.SQL("ALTER USER {} WITH LOGIN CREATEDB REPLICATION BYPASSRLS").format(sql.Identifier(username))
        )
        # print(f"✅ User '{username}' updated with privileges")
        rich_print(f"✅ User '{username}' updated with privileges", color="#00FF7F", bold=True)

        cur.close()
        conn.close()
        # print("🔒 Logged out from postgres superuser")
        rich_print("🔒 Logged out from postgres superuser", color="#00CED1")

    except Exception as e:
        # print("❌ Error (superuser connection):", e)
        rich_print("❌ Error (superuser connection):", color="#FF4500", bold=True)
        rich_print(str(e), color="#FF4500")
        return

    # Step 4: connect as new user and create database
    try:
        conn = psycopg2.connect(
            dbname="template1", user=username, password=password, host=HOST, port=PORT
        )
        conn.autocommit = True
        cur = conn.cursor()

        # --- NEW LOGIC: cek dulu apakah DB sudah ada
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
        if cur.fetchone():
            # print(f"⚠️ Database '{database}' already exists.")
            rich_print(f"⚠️ Database '{database}' already exists.", color="#FFFF00", bold=True)
            rich_print(f"❓ Do you want to DROP and recreate database '{database}'? [y/N]: ",
                       color="#FFFF00", bold=True, end="")
            choice = input().strip().lower()
            if choice == "y":
                try:
                    cur.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(database)))
                    # print(f"🗑️ Database '{database}' dropped")
                    rich_print(f"🗑️ Database '{database}' dropped", color="#FF4500", bold=True)
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
                    # print(f"✅ Database '{database}' recreated")
                    rich_print(f"✅ Database '{database}' recreated", color="#00FF7F", bold=True)
                except Exception as e:
                    # print(f"❌ Error dropping/creating database: {e}")
                    rich_print(f"❌ Error dropping/creating database: {e}", color="#FF4500", bold=True)
            else:
                # print(f"⏭️ Skipping database creation for '{database}'")
                rich_print(f"⏭️ Skipping database creation for '{database}'", color="#FFFF00", bold=True)
        else:
            try:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
                # print(f"✅ Database '{database}' created")
                rich_print(f"✅ Database '{database}' created", color="#00FF7F", bold=True)
            except errors.DuplicateDatabase:
                # print(f"⚠️ Database '{database}' already exists, skipping")
                rich_print(f"⚠️ Database '{database}' already exists, skipping", color="#FFFF00", bold=True)

        cur.close()
        conn.close()
        # print("🔒 Logged out from new user session")
        rich_print("🔒 Logged out from new user session", color="#00CED1")

    except Exception as e:
        if os.getenv("TRACEBACK", "0").lower() in ["1", "true", "yes"]:
            print(traceback.format_exc())
        else:
            # print("❌ Error (new user connection):", e)
            rich_print("❌ Error (new user connection):", color="#FF4500", bold=True)
            rich_print(str(e), color="#FF4500")


if __name__ == "__main__":
    main()
