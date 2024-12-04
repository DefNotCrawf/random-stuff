import bcrypt
import sqlite3 as sql
import getpass
import os
import time
import random
import uuid


def create_user():
    db_path = "./hashing/data/database.db"  # fix when moving to LoginFlask
    if not os.path.exists(db_path):
        print("Error: Database does not exist.")
        exit(1)

    con = sql.connect(db_path)
    cur = con.cursor()

    user_id = str(uuid.uuid4())
    username = input("Enter username: ")
    sampleDoB = input("Enter DoB: ")
    while True:
        password = getpass.getpass("Enter password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("Error: Passwords do not match.")
            continue
        else:
            break

    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    try:
        time.sleep(round(random.uniform(0.2, 0.4), 3))  # Decoy delay
        cur.execute(
            "INSERT INTO e50PMSBi_users (xQP9g_UUID, vX8hR_username, D9K66_password, nzqCh_DoB) VALUES (?, ?, ?, ?)",
            (user_id, username, hashed_password.decode(), sampleDoB),
        )
        con.commit()
        print("Record inserted successfully.")
    except sql.IntegrityError:
        time.sleep(round(random.uniform(0.2, 0.4), 3))  # Decoy delay
        print("Error: Could not insert the record due to a constraint violation.")
    except sql.OperationalError:
        time.sleep(round(random.uniform(0.2, 0.4), 3))  # Decoy delay
        print("Error: Operational error occurred while interacting with the database.")
    except sql.DatabaseError:
        time.sleep(round(random.uniform(0.2, 0.4), 3))  # Decoy delay
        print("Error: General database error occurred.")
    except Exception:
        time.sleep(round(random.uniform(0.2, 0.4), 3))  # Decoy delay
        print("An unexpected error occurred.")
    finally:
        con.close()


def create_UUID():
    print(f"{uuid.uuid4()}")


if __name__ == "__main__":
    create_user()
