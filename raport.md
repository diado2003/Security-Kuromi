# Raport â€” Break the Login: Atacarea È™i securizarea autentificÄƒrii

## Titlu & Identificare
- Nume proiect: Security-Kuromi
- Student: Diana-Ioana Dospinescu (username: diado2003 )
- Hostname VM: [hostname]

## Cuprins
1. Introducere
2. Setup mediu
3. Implementare MVP
4. Prezentare vulnerabilitÄƒÈ›i (mapping OWASP)
5. Demonstrare atacuri (PoC)
6. AnalizÄƒ impact
7. Implementare fix
8. Re-test (dovezi)
9. Audit & Logging
10. Concluzii
11. Anexe (capturi, scripturi, commit hashes, video)


## 1. Introducere

**Security-Kuromi** is a Flask API + Streamlit UI + SQLite DB application that has both backend and frontend. 

The **frontend** is made in streamlit and has 4 pages:

### 1.1 The login page, that either registers you or logs you in
### 1.2 Security Tools which are tools made by me after the book Ethical Hacking in Python. Those tools 
### help you find the domain, geolocating the ip, finding subdomains of a domain, and also finding the ports that are open.
### Also, they work in the ui: you just have to introduce the input values and the script runs.
### 1.3 I made a little Keylogger that you can either open from the ui or use the script.
### 1.4 Metadata page gives you the information behind either a .pdf or an image. You just have to upload a file that
### suits the data type requested from the user.

All the other scripts for attacks, keylogger, metadata, database and forensics were made using Python 3.12. All the important libraries are in requirements.txt.

- streamlit==1.55.0
- Flask==3.1.3
- requests==2.32.5
- toml==0.10.2
- bcrypt==5.0.0 
- streamlit-confetti-0.1.0
- whois==1.20240129.2
- ipinfo==5.6.0
- colorama==0.4.6
- python-whois-0.9.6
- keyboard==0.13.5
- pikepdf==10.5.1
- pillow==11.2.1

The **backend** has 2 components:

### 1.1 Flask:
Makes the bridge between the frontend and backend. 
It listens to the requests from the ui, it runs python logic - checking the database. 
Also it does the requests, routing, url handling.

In backend/app.py, I used Flask, also for hashing the passwords using **bcrypt** that the user introduces when registrating.
Then those passwords are stored in the database.

### 1.2 Database:
It has 2 tables: Audit and User Information which are in backend/db.py. It was made using the **sqlite3** library.

CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT NOT NULL DEFAULT 'USER',
            reset_token TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            locked INTEGER NOT NULL DEFAULT 0
        )

CREATE TABLE IF NOT EXISTS audit_logs(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action TEXT,
    resource_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)

The **tools** that i made with the help of Ethical Hacking in Python:

### 1.1 Domain, Subdomain, Geolocating IPs, Finding the ports that aren't used:

> WHOIS is a query and response protocol often used for querying
> databases that store registered domain names. 
> We can use the python-whois library to do that in Python.

> Finding subdomains of a particular website lets you explore its whole domain
> infrastructure. The technique we will use here is a dictionary attack; in other words, we will test
> all common subdomain names of that particular domain. Whenever we receive a
> response from the server, that's an indicator for us that the subdomain is alive.

His code was giving me this error:
    TimeoutError: [WinError 10060] A connection attempt failed because the connected party 
    did not properly respond after a period of time, or established connection failed because
    connected host has failed to respond
    During handling of the above exception, another exception occurred.

I modified it so if after 5s, there isn't a connection established, it just skips to the next word in the subdomain-100.txt.
On the author's github, there are even 1000 and 10 000 words for finding a domain.
Because it is time consuming (as you wait 10 000 light years) for it to finish running, i did stick with subdomain-100.txt. If needed, it can be changed easily to find even more subdomains.

### 1.2 Keylogger
> Keylogger is a type of surveillance technology used to monitor and record each keystroke 
> typed on a specific computer's keyboard. 
> It is also considered malware since it can be invisible running in the background, and 
> the user cannot notice the presence of this program.

> With a keylogger, you can easily use this for unethical purposes; you can register
> everything the user is typing on the keyboard, including credentials, private
> messages, etc., and send them back to you.

> Things to get started:
    -> keyboard module
    -> why?
        -> so it listens to keystrokes in the background.
        -> Whenever a key is pressed and released, we add it to a global string
        variable.
        -> Every N seconds, report the content of this string variable via email

> This module allows you to take complete control of your keyboard, hook global
> events, register hotkeys, simulate key presses, and much more, and it is a small
> module, though.

### 1.3 Forensics:

> Extracting Metadata from Files
    -> pikepdf library
    -> sys module to get the filename from the command-line arguments

I added a function so that the information can be read nicely by anyone:

    /Author : Editor
    /Producer : MicrosoftÂ® Word for Microsoft 365
    /ModDate : D:20260226222654+02'00'
    /Creator : MicrosoftÂ® Word for Microsoft 365
    /CreationDate : D:20260226222654+02'00'

> Extracting Image Metadata

> Devices such as digital cameras, smartphones, and scanners use the EXIF
> standard to save images or audio files. This standard contains many valuable
> tags to extract, which can be helpful for forensic investigation, such as the make,
> model of the device, the exact date and time of image creation, and even the GPS
> information on some devices.

>    -> Pillow 

Filename: metadata.png
Image Size: (769, 301)
Image Height: 301
Image Width: 769
Image Format: PNG
Image Mode: RGB
Image is Animated: False
Frames in Image: 1
Orientation: 1

Also i used a picture of his to see i get all the same information and i did.

Filename: image.jpg
Image Size: (5312, 2988)
Image Height: 2988
Image Width: 5312
Image Format: JPEG
Image Mode: RGB
Image is Animated: False
Frames in Image: 1
ImageWidth: 5312
ImageLength: 2988
ResolutionUnit: 2
ExifOffset: 226
Make: samsung
Model: SM-G920F
Software: G920FXXS4DPI4
Orientation: 1
DateTime: 2016:11:10 19:33:22
YCbCrPositioning: 1
XResolution: 72.0
YResolution: 72.0


## 2. Setup mediu

 The application has two main components:
  - Flask backend, responsible for authentication, password reset, sessions and audit logging;
  - Streamlit frontend, used as a simple UI for registration, login and security tools.

2.1 Environment / Requirements

Environment used:
  - Python: 3.12
  - Database: SQLite
  - Backend framework: Flask
  - Frontend framework: Streamlit
  - Password hashing: bcrypt
  - Testing tools: curl, PowerShell, browser developer tools
  - Version control: Git

2.2 Project Setup Commands

From the parent folder:
>    cd "C:\Users\diana\OneDrive\Desktop\PROIECT SECURITATE"
Clone/open project:
>    cd Security-Kuromi
Check Python:
>    python --version
>    pip --version
Create virtual environment:
>    python -m venv .venv
>    .\.venv\Scripts\Activate.ps1
If PowerShell blocks activation:
>    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
>    .\.venv\Scripts\Activate.ps1
Install dependencies:
>    pip install --upgrade pip
>    pip install -r requirements.txt
Verify important libraries:
>    python -c "import flask, streamlit, bcrypt, requests; print('Dependencies OK')"

2.3 Environment Variables

The application uses environment variables for secrets. These values are not hardcoded in production. For the local
laboratory setup, I used temporary PowerShell variables.

Commands:

>  $env:FLASK_SECRET_KEY="change-this-secret-in-production"
>  $env:ADMIN_REGISTER_SECRET="admin-lab-secret"
>  $env:FLASK_DEBUG="0"

Optional verification:

>  echo $env:FLASK_SECRET_KEY
>  echo $env:ADMIN_REGISTER_SECRET
>  echo $env:FLASK_DEBUG

2.4 Database Initialization

The project uses SQLite. The database file is `users.db`, located in the root of the project. The backend schema creates
two tables: `users` and `audit_logs`.

Initialize DB:

>  cd backend
>  python db.py

Expected output idea:

DB schema verified. Migrated 0 plaintext passwords to bcrypt.
Check DB file exists:

>  cd ..
>  Get-Item .\users.db

Optional inspect tables:

>  python -c "import sqlite3; c=sqlite3.connect('users.db'); print(c.execute(\"SELECT name FROM sqlite_master WHERE
>  type='table'\").fetchall()); c.close()"

2.5 Running the Backend

>  cd "C:\Users\diana\OneDrive\Desktop\PROIECT SECURITATE\Security-Kuromi\backend"
>  $env:FLASK_SECRET_KEY="change-this-secret-in-production"
>  $env:ADMIN_REGISTER_SECRET="admin-lab-secret"
>  $env:FLASK_DEBUG="0"
>  python app.py

Expected:

  Running on http://127.0.0.1:5000

  Quick backend test:

  curl http://127.0.0.1:5000/protected

  Expected unauthenticated response:

  {"error":"Not authenticated"}

2.6 Running the Frontend

  Terminal 2:

>  cd "C:\Users\diana\OneDrive\Desktop\PROIECT SECURITATE\Security-Kuromi\frontend"
>  ..\ .venv\Scripts\Activate.ps1
>  streamlit run site.py

If using project root .venv, use:

>  cd "C:\Users\diana\OneDrive\Desktop\PROIECT SECURITATE\Security-Kuromi"
>  .\.venv\Scripts\Activate.ps1
>  streamlit run frontend\site.py

  Expected:

  Local URL: http://localhost:8501

2.7 First Functional Test

  Register user:

>  curl -X POST http://127.0.0.1:5000/register `
>    -H "Content-Type: application/json" `
>    -d "{\"email\":\"diana@example.com\",\"username\":\"diana\",\"password\":\"Test123!\"}"

  Login:

>  curl -i -X POST http://127.0.0.1:5000/login `
>    -H "Content-Type: application/json" `
>    -d "{\"username\":\"diana\",\"password\":\"Test123!\"}"

  Mention:

  The `-i` flag was used to display response headers, including the `Set-Cookie` header used later for session hardening
  verification.



## 3. MVP Implementation

The MVP is not some huge enterprise app, because that was not the point here. The point was to build a normal login system, show how it can be attacked, and then fix the exact problems.

The main features are:
- `register` - creates a new user account with email, username, password and role.
- `login` - checks the credentials and starts a session.
- `logout` - clears the session.
- `forgot-password` - starts the password reset flow.
- `reset-password` - changes the password using a reset token.
- `protected` - a simple route used to test if the user is logged in.

Technologies used:
- Flask for the backend API.
- SQLite for the database.
- bcrypt for password hashing.
- Streamlit for the frontend demo.
- curl / PowerShell / Python scripts for testing the attacks.

The backend logic is mostly in `backend/app.py`. The database setup is in `backend/db.py`. The attack scripts are in `attacks/`.

### 3.1 Backend Routes

_____________________________________________________________________
| Method | Route              | What it does                        |
| `POST` | `/register`        | creates a new account               |
| `POST` | `/login`           | logs in a user                      |
| `POST` | `/logout`          | logs out a user                     |
| `POST` | `/forgot-password` | requests a password reset           |
| `POST` | `/reset-password`  | resets the password                 |
| `GET`  | `/protected`       | checks if the user is authenticated |
---------------------------------------------------------------------

### 3.2 Database Schema

The app uses SQLite and the database file is `users.db`.

`users` table:

```sql
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT NOT NULL DEFAULT 'USER',
    reset_token TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    locked INTEGER NOT NULL DEFAULT 0
);
```

In the fixed version, the app also uses these columns for safe password reset:

```sql
ALTER TABLE users ADD COLUMN reset_token_hash TEXT;
ALTER TABLE users ADD COLUMN reset_token_expires_at TEXT;
```

`audit_logs` table:

```sql
CREATE TABLE IF NOT EXISTS audit_logs(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    action TEXT,
    resource_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Screenshots used for the MVP / DB part:
- `from raw passwords to bcrypt.png`
- `bcrypt passwords v02.png`
- `dupa bcrypt + time insert pwd.png`
- `added another user.png`
- `the user i added - n bcrypt that pwd too.png`

## 4. Vulnerabilities Presentation (OWASP Mapping)

The vulnerable version had basic authentication problems. They are not fancy, but they are exactly the kind of problems that make login systems easy to break.

### 4.1 Unsafe Password Storage

Vulnerability: passwords were stored or handled unsafely.
Technical description: if passwords are stored in plaintext or not handled with a strong hashing algorithm, anyone who gets access to the database can see or crack user passwords. This is bad even for a small project, because database files and backups can be leaked.

OWASP mapping:
- OWASP Top 10 2021: A07 - Identification and Authentication Failures

### 4.2 Weak Password Policy

Vulnerability: the app accepted weak passwords like `123`, `123456`, `password`, etc.
Technical description: if the app accepts weak passwords, an attacker can guess accounts much easier. The app should reject passwords that are obviously bad.
OWASP mapping:
- OWASP Top 10 2021: A07 - Identification and Authentication Failures

### 4.3 Brute Force / No Rate Limiting

Vulnerability: login attempts were not limited.
Technical description: an attacker could send many login requests with different passwords. Without lockout, delay, or rate limiting, the backend allows unlimited guessing.

OWASP mapping:
- OWASP Top 10 2021: A07 - Identification and Authentication Failures

### 4.4 User Enumeration

Vulnerability: the reset password flow could reveal if a username exists.
Technical description: if `/forgot-password` gives different answers or very different response times for real users and fake users, an attacker can build a list of valid usernames.

OWASP mapping:
- OWASP Top 10 2021: A07 - Identification and Authentication Failures

### 4.5 Insecure Session Cookies

Vulnerability: session cookies did not have enough security flags.
Technical description: cookies should use `HttpOnly`, `Secure`, and `SameSite`. These flags reduce the chance of cookie theft and cookie abuse.

OWASP mapping:
- OWASP Top 10 2021: A05 - Security Misconfiguration
- OWASP Top 10 2021: A07 - Identification and Authentication Failures

### 4.6 Unsafe Password Reset

Vulnerability: password reset tokens were predictable or exposed.
Technical description: if the token is something like `reset-diana`, an attacker can guess it, reset the victim password, and login as that user.

OWASP mapping:
- OWASP Top 10 2021: A07 - Identification and Authentication Failures

## 5. Attack Demonstration (PoC)

For the PoC part, I used scripts from the `attacks/` folder. They are simple because I wanted the output to be easy to understand.
Run the backend first:

```powershell
cd "C:\Users\diana\OneDrive\Desktop\PROIECT SECURITATE\Security-Kuromi\backend"
python app.py
```

Then run the attacks from the project folder:

```powershell
cd "C:\Users\diana\OneDrive\Desktop\PROIECT SECURITATE\Security-Kuromi"
```

### 5.1 Weak Password / Unsafe Storage PoC

Script:

```powershell
python attacks\weak-attacks.py --expected vulnerable
```

Manual request:

```powershell
curl -X POST http://127.0.0.1:5000/register `
  -H "Content-Type: application/json" `
  -d "{\"email\":\"weak@example.com\",\"username\":\"weakdemo\",\"password\":\"123\"}"
```

Expected vulnerable output:

```text
Status: 200
Response: {"success": true}
```

Why it works: the vulnerable version accepts a weak password instead of blocking it. Also, if the password is stored badly, opening the database is enough to expose the account password.

Screenshots:
- `from raw passwords to bcrypt.png`
- `bcrypt passwords v02.png`

### 5.2 Brute Force PoC

Script:

```powershell
python attacks\bruteforce.py --username diana --expected vulnerable
```

Manual request:

```powershell
curl -X POST http://127.0.0.1:5000/login `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"diana\",\"password\":\"123456\"}"
```

Expected vulnerable output:

```text
Status: 401, Response: {"success": false, "error": "Invalid credentials"}
Status: 401, Response: {"success": false, "error": "Invalid credentials"}
Status: 200, Response: {"success": true, "username": "diana", "role": "USER"}
```

Why it works: the vulnerable backend lets the attacker try password after password. There is no lockout, so the script can continue until it gets lucky.

Screenshot:
- `bruteforce v02.png`

### 5.3 User Enumeration PoC

Script:

```powershell
python attacks\enumeration.py --existing diana --missing randomuser --expected vulnerable
```

Manual requests:

```powershell
curl -X POST http://127.0.0.1:5000/forgot-password `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"diana\"}"
```

```powershell
curl -X POST http://127.0.0.1:5000/forgot-password `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"randomuser\"}"
```

Expected vulnerable output:

```text
Existing user: different response body or different timing
Missing user: different response body or different timing
```

Why it works: if the app answers differently for existing and non-existing users, the attacker can discover real usernames.

### 5.4 Password Reset Takeover PoC

Script:

```powershell
python attacks\reset-attack.py --victim diana --expected vulnerable
```

What the script does:
- sends `/forgot-password` for `diana`
- guesses a token like `reset-diana`
- sends `/reset-password`
- tries to login with the new password

Expected vulnerable output:

```text
[1] Trigger forgot-password for victim...
status: 200

[2] Use predicted token: reset-diana
status: 200

[3] Verify takeover by logging in with victim + new password...
status: 200
```

Why it works: the reset token is predictable, so the attacker does not need access to the victim email.

Screenshot:
- `reset-attack v02.png`

### 5.5 Session Cookie PoC

Command:

```powershell
curl -i -X POST http://127.0.0.1:5000/login `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"diana\",\"password\":\"Test123!\"}"
```

In the vulnerable version, the `Set-Cookie` header is missing important flags.

Bad example:

```text
Set-Cookie: session=...
```

The problem is that it should include `HttpOnly`, `Secure`, and `SameSite`.

## 6. Impact Analysis

**Unsafe password storage impact**: if the database gets leaked, the attacker gets passwords or password hashes that are too easy to attack. If the user reused the same password somewhere else, that becomes a bigger problem.
**Weak password policy impact**: users can create accounts with passwords that are basically free for attackers. This can lead to account takeover.
**Brute force impact**: the attacker can automate login attempts until one password works. This also creates noise and can overload the app.
**User enumeration impact**: the attacker can find valid usernames. That does not give full access by itself, but it makes brute force and reset attacks much easier.
**Insecure session cookie impact**: weak cookie settings make session theft or abuse easier. If the attacker gets a valid session, they do not need the password anymore.
**Unsafe password reset impact**: this can give full account takeover. If the attacker can predict or steal the reset token, they can change the victim password.

## 7. Fix Implementation

Most fixes were made in `backend/app.py`. The database schema and migration logic are in `backend/db.py`.
Current local branch:

```text
master
```

Current local commit:

```text
8a121f9 Add raport README
```

For final submission, I still need two clear versions:
- `vulnerable` - before fixes
- `fixed` or `master` - after fixes

### 7.1 bcrypt Password Hashing

Files:
- `backend/app.py`
- `backend/db.py`

Code:

```python
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
```

The fixed version stores bcrypt hashes, not raw passwords. It also migrates old plaintext passwords to bcrypt when the database script runs.
Why it stops the attack: opening the database does not show the real password anymore.

### 7.2 Password Policy

File:
- `backend/app.py`

Code:

```python
def validate_password_strength(password: str) -> bool:
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    return has_upper and has_lower and has_digit and has_special
```

Why it stops the attack: passwords like `123` or `password` are rejected.

### 7.3 Brute Force Protection

File:
- `backend/app.py`

Code:

```python
MAX_FAILED_ATTEMPTS = 5
LOCK_WINDOW_MINUTES = 15
```

The app counts failed logins in `audit_logs`. After too many failures, it locks the account and returns `429`.
Why it stops the attack: the attacker cannot try unlimited passwords.

### 7.4 Generic Login Errors

File:
- `backend/app.py`

The app returns the same kind of error for wrong username and wrong password:

```json
{"success": false, "error": "Invalid credentials"}
```

Why it helps: the attacker does not get free hints.

### 7.5 Safe Password Reset Tokens

File:
- `backend/app.py`

Code:

```python
token = secrets.token_urlsafe(32)
token_hash = hash_reset_token(token)
expires_at = (now_utc() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)).isoformat()
```

The fixed version:
- generates a random token
- stores only the hash of the token
- expires it after 15 minutes
- does not return the token in the response

Why it stops the attack: `reset-diana` or any guessed token will not work anymore.

### 7.6 User Enumeration Fix

File:
- `backend/app.py`

Code:

```python
FORGOT_RESPONSE_DELAY_SECONDS = 0.35
LOGIN_RESPONSE_DELAY_SECONDS = 0.45
```

The forgot password response is generic:

```json
{"success": true, "message": "If the user exists, a reset token was generated."}
```

Why it helps: real and fake users get the same response shape and similar timing.

### 7.7 Cookie Flags

File:
- `backend/app.py`

Code:

```python
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=20)
```

Why it helps: the session cookie is harder to steal or abuse.

## 8. Re-test Evidence

After fixing the app, I ran the same attacks again. The point was to prove the old attacks fail now.

### 8.1 Weak Password Re-test

Command:

```powershell
python attacks\weak-attacks.py --expected fixed
```

Expected fixed output:

```text
POST /register username='weakdemo...' password='123'
Status: 400
Response: {'success': False, 'error': 'Parola trebuie sa aiba cel putin 8 caractere...'}

DB password sample:
diana: $2b$...

=== Result ===
PASS
```

Before: weak password accepted.

After: weak password rejected and passwords are bcrypt hashes.

### 8.2 Brute Force Re-test

Command:

```powershell
python attacks\bruteforce.py --username diana --expected fixed
```

Expected fixed output:

```text
Status: 401, Response: {'success': False, 'error': 'Invalid credentials'}
Status: 401, Response: {'success': False, 'error': 'Invalid credentials'}
Status: 429, Response: {'success': False, 'error': 'Invalid credentials'}
Lockout triggered: too many failed login attempts.

=== Result ===
PASS
```

Before: unlimited attempts.

After: lockout after too many failed attempts.

### 8.3 User Enumeration Re-test

Command:

```powershell
python attacks\enumeration.py --existing diana --missing randomuser --expected fixed
```

Expected fixed output:

```text
[diana sample 1] status=200 body={"success":true,"message":"If the user exists, a reset token was generated.",...}
[randomuser sample 1] status=200 body={"success":true,"message":"If the user exists, a reset token was generated.",...}

Average existing=...
Average missing=...
delta=...

=== Result ===
PASS
```

Before: different responses or timing.

After: same response shape and similar timing.

### 8.4 Password Reset Re-test

Command:

```powershell
python attacks\reset-attack.py --victim diana --expected fixed
```

Expected fixed output:

```text
[1] Trigger forgot-password for victim...
status: 200
body: {"success":true,"message":"If the user exists, a reset token was generated.","expires_in_minutes":15}

[2] Use predicted token: reset-diana
status: 400
body: {"success":false,"error":"Token invalid sau expirat."}

[3] Verify takeover by logging in with victim + new password...
status: 401

=== Result ===
PASS
```

**Before**: predictable token worked.
**After**: predicted token is rejected.

### 8.5 Cookie Re-test

Command:

```powershell
curl -i -X POST http://127.0.0.1:5000/login `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"diana\",\"password\":\"Test123!\"}"
```

Expected fixed header:

```text
Set-Cookie: session=...; Secure; HttpOnly; Path=/; SameSite=Lax
```

**Before**: cookie flags were missing or weaker.
**After**: cookie has the security flags.

## 9. Audit & Logging

I added audit logging because without logs I cannot prove what happened. For security work, logs are not optional.

Events logged:
- `register_success`
- `failed_login`
- `failed_login_unknown_user`
- `login_success`
- `login_locked`
- `password_reset_requested`
- `password_reset_completed`
- `logout`

The logs are stored in `audit_logs`.

Columns:
- `id`
- `user_id`
- `action`
- `resource_id`
- `timestamp`
- `ip_address`

### 9.1 Latest Logs

```powershell
python -c "import sqlite3; c=sqlite3.connect('users.db'); rows=c.execute('SELECT id,user_id,action,resource_id,timestamp,ip_address FROM audit_logs ORDER BY id DESC LIMIT 20').fetchall(); [print(r) for r in rows]; c.close()"
```

### 9.2 Failed Login Attempts

```sql
SELECT user_id, resource_id, COUNT(*) AS attempts
FROM audit_logs
WHERE action='failed_login'
GROUP BY user_id, resource_id;
```

PowerShell version:

```powershell
python -c "import sqlite3; c=sqlite3.connect('users.db'); rows=c.execute(\"SELECT user_id, resource_id, COUNT(*) FROM audit_logs WHERE action='failed_login' GROUP BY user_id, resource_id\").fetchall(); [print(r) for r in rows]; c.close()"
```

### 9.3 Password Reset Trail

```sql
SELECT user_id, action, timestamp, ip_address
FROM audit_logs
WHERE action IN ('password_reset_requested', 'password_reset_completed')
ORDER BY timestamp DESC;
```

### 9.4 Login / Logout Trail

```sql
SELECT user_id, action, timestamp, ip_address
FROM audit_logs
WHERE action IN ('login_success', 'logout')
ORDER BY timestamp DESC;
```

This gives me a basic audit trail: failed logins, successful logins, reset requests, completed resets and logout events.

## 10. Conclusions & Lessons Learned

This project showed me that authentication is not just checking a username and password. That is the easy part. The annoying but important part is everything around it: password storage, reset tokens, brute force protection, cookies and logs.

What I learned:
- bcrypt should be used for passwords, no excuses.
- weak passwords make attacks way easier.
- password reset is dangerous if the token is predictable.
- brute force protection is needed even in a small app.
- user enumeration looks small but helps attackers a lot.
- logs matter because they show what actually happened.

Limitations:
- This is still a lab project, not a full production auth system.
- There is no real email integration for reset links.
- SQLite is fine for demo, but not ideal for a bigger deployed app.
- The rate limiting is local DB based, not Redis or a production rate limiter.
- `SESSION_COOKIE_SECURE=True` is correct for HTTPS, but for local HTTP testing it can be annoying.

Next steps:
- add real email sending for reset links
- add CSRF protection
- add automated tests
- create proper `vulnerable` and `fixed` branches/tags
- export the report as PDF
- record the 5-10 minute demo video

## 11. Annexes

Screenshots included in `Security-Kuromi/screenshots/`:
- `added another user.png`
- `bcrypt passwords v02.png`
- `bruteforce v02.png`
- `dupa bcrypt + time insert pwd.png`
- `from raw passwords to bcrypt.png`
- `reset-attack v02.png`
- `the user i added - n bcrypt that pwd too.png`

PoC scripts included in `Security-Kuromi/attacks/`:
- `weak-attacks.py`
- `bruteforce.py`
- `enumeration.py`
- `reset-attack.py`

Video link:
- `[add YouTube/Dropbox/Drive link here]`

Suggested video timestamps:
- `00:00 - 00:45` project setup and app overview
- `00:45 - 02:30` vulnerable attacks
- `02:30 - 04:30` fixes in code
- `04:30 - 06:30` re-test after fixes
- `06:30 - 07:00` conclusions

Commit hashes:
- vulnerable branch/tag: `[add vulnerable hash here]`
- fixed branch/tag: `8a121f9` / `master`

---

## Checklist obligatoriu (pentru predare)
- [ ] Raport >= 20 pagini
- [ ] Capturi cu username & hostname & prompt & date/time
- [ ] Doua versiuni in repo: `vulnerable` si `fixed` (branch/tag)
- [ ] Clip video 5-10 minute
- [ ] VM evidence (hostname in screenshots)

---

### Quick screenshot instructions
- Terminal: include full prompt, command, output, `whoami` and `hostname` in the screenshot.
- Burp/Postman: include raw request and raw response.

---

