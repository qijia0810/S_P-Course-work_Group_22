# simulate_attack_password_leak.py
from models import db, User
from app import app

def simulate_password_leak_attack():
    with app.app_context():
        print("Simulate an attacker accessing a database and reading all user information...\n")
        users = User.query.all()
        for user in users:
            print(f"username: {user.username}, email: {user.email}, plain text password: {user.password_hash}")

if __name__ == '__main__':
    simulate_password_leak_attack()
