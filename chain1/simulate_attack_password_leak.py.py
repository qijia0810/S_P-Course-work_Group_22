# simulate_attack_password_leak.py
# This version simulates a realistic external attacker who has direct access to the SQLite file (no Flask context).

import sqlite3

DB_PATH = 'instance/bidding.db'  # Adjust path if your SQLite DB is elsewhere

def simulate_password_leak_attack():
    print("[!] Simulating attacker reading raw SQLite database without Flask context...\n")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT username, email, password_hash FROM users")
        rows = cursor.fetchall()

        for row in rows:
            username, email, password_hash = row
            print(f"username: {username}, email: {email}, leaked password field: {password_hash}")

        conn.close()
    except Exception as e:
        print(f"[-] Error accessing database: {e}")


if __name__ == '__main__':
    simulate_password_leak_attack()
