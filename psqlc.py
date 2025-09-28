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


HOST = "222.222.222.5"

def main():
    parser = argparse.ArgumentParser(description="Create PostgreSQL user and database.", formatter_class=CustomRichHelpFormatter)
    parser.add_argument("CONFIG", help="Format NEW_USERNAME NEW_PASSWORD NEW_DB", nargs=3)
    parser.add_argument("-u", "--username", help="New PostgreSQL username")
    parser.add_argument("-p", "--password", help="Password for new user")
    parser.add_argument("-d", "--database", help="Database name to create")
    parser.add_argument('-H', "--hostname", help=f"Postgresql Server address/hostname/ip, default={HOST}", default=HOST)
    parser.add_argument('-U', "--user", help="Postgresql Server password admin, default='postgres'", default='postgres')
    parser.add_argument('-P', "--passwd", help="Postgresql Server password admin")

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)

    args = parser.parse_args()

    if args.CONFIG:
        username, password, database = args.CONFIG
    else:
        username = args.username
        password = args.password
        database = args.database

    # Step 1: connect as postgres superuser
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=args.user,
            host=args.hostname,
        )
        if password:
            conn = psycopg2.connect(
                dbname="postgres",
                user=args.user,
                host=args.hostname,
                password=args.passwd
            )   
        conn.autocommit = True
        cur = conn.cursor()

        # Step 2: create user
        try:
            cur.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(username)
                ),
                [password],
            )
            print(f"✅ User '{username}' created")
        except errors.DuplicateObject:
            print(f"⚠️ User '{username}' already exists, skipping")

        # Step 3: alter user privileges
        cur.execute(
            sql.SQL(
                "ALTER USER {} WITH LOGIN CREATEDB REPLICATION BYPASSRLS"
            ).format(sql.Identifier(username))
        )
        print(f"✅ User '{username}' updated with privileges")

        cur.close()
        conn.close()
        print("🔒 Logged out from postgres superuser")

    except Exception as e:
        print("❌ Error (superuser connection):", e)
        return

    # Step 4: connect as new user and create database
    try:
        conn = psycopg2.connect(
            dbname="template1",
            user=username,
            password=password,
            host=HOST,
        )
        conn.autocommit = True
        cur = conn.cursor()

        try:
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database))
            )
            print(f"✅ Database '{database}' created")
        except errors.DuplicateDatabase:
            print(f"⚠️ Database '{database}' already exists, skipping")

        cur.close()
        conn.close()
        print("🔒 Logged out from new user session")

    except Exception as e:
        if os.getenv('TRACEBACK', '0').lower() in ['1', 'true', 'yes']:
            print(traceback.format_exc())
        else:
            print("❌ Error (new user connection):", e)


if __name__ == "__main__":
    main()
