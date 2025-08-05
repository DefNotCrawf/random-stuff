import sqlite3 as sqlite
import argon2
from dotenv import load_dotenv

import os
import getpass
import uuid
import datetime

load_dotenv()

DATABASE_PATH: str = "./arg_hashing/user.db"


def validate_database_structure():
    """Validate that the database has the correct table structure."""
    if not os.path.exists(DATABASE_PATH):
        print(f"Database at {DATABASE_PATH} does not exist.")
        return False

    con = sqlite.connect(database=DATABASE_PATH)
    cur = con.cursor()

    try:
        # Check if the table exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='As8JS_users';"
        )
        table_exists = cur.fetchone()

        if not table_exists:
            print("Table 'As8JS_users' does not exist.")
            con.close()
            return False

        # Get table schema
        cur.execute("PRAGMA table_info(As8JS_users);")
        columns = cur.fetchall()

        # Expected columns: (cid, name, type, notnull, dflt_value, pk)
        expected_columns = {
            "c9ujs_uuid": {"type": "TEXT", "notnull": 0, "pk": 1},
            "as9uc_username": {"type": "TEXT", "notnull": 1, "pk": 0},
            "q2c3S_email": {"type": "TEXT", "notnull": 1, "pk": 0},
            "ASCiS_password": {"type": "TEXT", "notnull": 1, "pk": 0},
            "ACWws_DoB": {"type": "TEXT", "notnull": 1, "pk": 0},
            "1d383_permission": {"type": "TEXT", "notnull": 1, "pk": 0},
        }

        # Validate each column
        for column in columns:
            cid, name, col_type, notnull, dflt_value, pk = column

            if name not in expected_columns:
                print(f"Unexpected column found: {name}")
                con.close()
                return False

            expected = expected_columns[name]
            if col_type != expected["type"]:
                print(
                    f"Column {name} has wrong type: expected {expected['type']}, got {col_type}"
                )
                con.close()
                return False

            if notnull != expected["notnull"]:
                print(
                    f"Column {name} has wrong NOT NULL constraint: expected {expected['notnull']}, got {notnull}"
                )
                con.close()
                return False

            if pk != expected["pk"]:
                print(
                    f"Column {name} has wrong PRIMARY KEY constraint: expected {expected['pk']}, got {pk}"
                )
                con.close()
                return False

        # Check if all expected columns exist
        found_columns = {col[1] for col in columns}
        missing_columns = set(expected_columns.keys()) - found_columns
        if missing_columns:
            print(f"Missing columns: {missing_columns}")
            con.close()
            return False

        # Check UNIQUE constraints
        cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='As8JS_users';"
        )
        create_sql = cur.fetchone()[0]

        if "as9uc_username TEXT UNIQUE" not in create_sql:
            print("Username column missing UNIQUE constraint")
            con.close()
            return False

        if "q2c3S_email TEXT UNIQUE" not in create_sql:
            print("Email column missing UNIQUE constraint")
            con.close()
            return False

        print("Database structure validation passed.")
        con.close()
        return True

    except sqlite.OperationalError as e:
        print(f"Error validating database structure: {e}")
        con.close()
        return False
    except Exception as e:
        print(f"Unexpected error during validation: {e}")
        con.close()
        return False


def create_table():
    if not os.path.exists(DATABASE_PATH):
        print(f"Database at {DATABASE_PATH} does not exist: Creating database.")
        con = sqlite.connect(database=DATABASE_PATH)
        cur = con.cursor()
        try:
            cur.execute(
                """
                CREATE TABLE As8JS_users (
                    c9ujs_uuid TEXT PRIMARY KEY,
                    as9uc_username TEXT UNIQUE NOT NULL,
                    q2c3S_email TEXT UNIQUE NOT NULL,
                    ASCiS_password TEXT NOT NULL,
                    ACWws_DoB TEXT NOT NULL,
                    1d383_permission TEXT NOT NULL
                );
                """
            )
            print("Table created.")
            con.close()
        except sqlite.OperationalError as e:
            print(f"Error 'sqlite.OperationalError' occurred: {e}")
            con.close()
        except Exception as e:
            print(f"Unexpected error recreating database: {e}")
            con.close()
    else:
        print(f"Database already exists at '{DATABASE_PATH}'")
        # Validate the existing database structure
        if not validate_database_structure():
            print("Database structure is invalid. Recreating database...")
            os.remove(DATABASE_PATH)
            con = sqlite.connect(database=DATABASE_PATH)
            cur = con.cursor()
            try:
                cur.execute(
                    """
                    CREATE TABLE As8JS_users (
                        c9ujs_uuid TEXT PRIMARY KEY,
                        as9uc_username TEXT UNIQUE NOT NULL,
                        q2c3S_email TEXT UNIQUE NOT NULL,
                        ASCiS_password TEXT NOT NULL,
                        ACWws_DoB TEXT NOT NULL,
                        1d383_permission TEXT NOT NULL
                    );
                    """
                )
                print("Database recreated successfully.")
                con.close()
            except sqlite.OperationalError as e:
                print(f"Error recreating database: {e}")
                con.close()
            except Exception as e:
                print(f"Unexpected error recreating database: {e}")
                con.close()
        else:
            print("Database structure is valid.")


def create_admin_login():
    con = sqlite.connect(database=DATABASE_PATH)
    cur = con.cursor()

    admin_details = {
        "admin_username": os.getenv("admin_username"),
        "admin_email": os.getenv("admin_email"),
        "admin_password": os.getenv("admin_password"),
        "admin_dob": os.getenv("admin_dob"),
        "admin_permission": os.getenv("admin_permission", "admin"),
    }

    try:
        pass
    except Exception as e:
        print(f"Unexpected error creating default login: {e}")
    finally:
        con.close()


if __name__ == "__main__":
    create_table()
