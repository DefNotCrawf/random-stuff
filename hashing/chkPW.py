import sqlite3 as sql
import bcrypt
import getpass
import os
import time
import random

def checkPW():
    db_path = "./hashing/data/database.db"
    if not os.path.exists(db_path):
        print("Error: Database does not exist.")
        exit(1)

    con = sql.connect(db_path)
    cur = con.cursor()

    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    # Decoy delay before checking the database
    time.sleep(round(random.uniform(0.2, 0.4), 3))

    cur.execute(
        "SELECT vX8hR_username, D9K66_password FROM e50PMSBi_users WHERE vX8hR_username = ?",
        (username,),
    )
    user = cur.fetchone()

    if user:
        # Decoy delay before checking the password
        time.sleep(round(random.uniform(0.2, 0.4), 3))
        if bcrypt.checkpw(password.encode("utf-8"), user[1].encode("utf-8")):
            print("Password matched")
        else:
            time.sleep(
                round(random.uniform(0.2, 0.4), 3)
            )  # Decoy delay before printing password mismatch
            print("Password did not match")
    else:
        time.sleep(
            round(random.uniform(0.2, 0.4), 3)
        )  # Decoy delay before printing username mismatch
        print("Username did not match")

    con.close()

if __name__ == "__main__":
    checkPW()