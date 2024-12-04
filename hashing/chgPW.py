import sqlite3 as sql
import bcrypt
import getpass
import time
import os
import random


def changePW():
    db_path = "./hashing/data/database.db"
    if not os.path.exists(db_path):
        print("Error: Database does not exist.")
        exit(1)

    con = sql.connect(db_path)
    cur = con.cursor()

    username = input("Enter username: ")
    DoB = input("Enter DoB: ")

    # Decoy delay before checking the database
    time.sleep(round(random.uniform(0.2, 0.4), 3))

    cur.execute(
        "SELECT vX8hR_username, nzqCh_DoB FROM e50PMSBi_users WHERE vX8hR_username = ? AND nzqCh_DoB = ?",
        (username, DoB),
    )
    user = cur.fetchone()

    while True:
        if user:
            time.sleep(round(random.uniform(0.2, 0.4), 3))
            print("Username/DoB matched.")
            newPass = getpass.getpass("Enter new password: ")
            confirmPass = getpass.getpass("Confirm new password: ")
            if newPass != confirmPass:
                time.sleep(
                    round(random.uniform(0.2, 0.4), 3)
                )  # Decoy delay before printing password mismatch
                print("Password did not match.")
                continue

            salt = bcrypt.gensalt(rounds=12)
            hashed_password = bcrypt.hashpw(newPass.encode("utf-8"), salt)
            cur.execute(
                "UPDATE e50PMSBi_users SET D9K66_password = ? WHERE vX8hR_username = ? AND nzqCh_DoB = ?",
                (hashed_password.decode(), username, DoB),
            )
            con.commit()
            print("Password updated successfully.")
            break
        else:
            time.sleep(
                round(random.uniform(0.2, 0.4), 3)
            )  # Decoy delay before printing username/DoB mismatch
            print("Username/DoB did not match.")
            break
    con.close()

if __name__ == "__main__":
    changePW()