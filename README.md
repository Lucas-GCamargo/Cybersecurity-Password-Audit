# 🔐 Cybersecurity Password Audit Tool

[![Python](https://img.shields.io/badge/Language-Python_3-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Security](https://img.shields.io/badge/Domain-Cybersecurity-red?style=for-the-badge&logo=hackthebox)](https://www.cyber.gov.au)
[![Hashing](https://img.shields.io/badge/Algorithm-SHA--256-orange?style=for-the-badge&logo=letsencrypt)](https://en.wikipedia.org/wiki/SHA-2)
[![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)](https://github.com/Lucas-GCamargo/Cybersecurity-Password-Audit)

> **A Python-based password auditing tool that identifies weak or compromised password hashes within a user database — simulating the internal credential audit process used by security teams to detect at-risk accounts before attackers do.**

---

## ⚠️ Ethical Use Disclaimer

**This tool was built strictly for educational and authorised security auditing purposes.**

- This script must only ever be run against data you own or have explicit written permission to audit
- Running this tool against real systems or users without authorisation is illegal under the **Australian Criminal Code Act 1995 (Cth) — s477.1 Unauthorised access to, or modification of, restricted data**
- The `rockyou.txt` wordlist is a publicly available research dataset widely used across the cybersecurity industry for password strength evaluation
- **No real user credentials were used in the development or testing of this project — all user data is mock/synthetic**

**If you are unsure whether you have authorisation — you do not. Do not run this tool.**

---

## 📌 The Security Problem

Organisations store passwords as hashes rather than plain text. However, this alone does not guarantee safety. Weak passwords — even when hashed — remain vulnerable because attackers can pre-compute hashes for millions of common passwords and compare them directly against a stolen database. This is known as a **dictionary attack**.

This project simulates that exact attack from a **defensive perspective**: identifying which accounts in a user database are at risk *before* an external threat actor exploits them.

**Real-world context:** The `rockyou.txt` wordlist originates from a 2009 breach of the RockYou social platform in which 32 million plaintext passwords were exposed. It has since become the industry standard wordlist for password auditing and penetration testing.

---

## 🔍 How It Works

```
user_data.json  ←  Simulated user database with hashed passwords
        ↓
load_user_data()          reads and parses JSON
        ↓
load_common_passwords()   loads wordlist (rockyou.txt, falls back to rockyou_sample.txt)
        ↓
build_hash_dict()         pre-computes a hash→plaintext dictionary
        ↓
check_passwords()         O(1) lookup per user — matched = vulnerable
        ↓
save_results()            writes findings to output.json
        ↓
interactive_mode()        real-time SHA-256 hashing — run with --interactive flag
```

---

## 🛠️ Technical Concepts Demonstrated

| Concept | Implementation |
|---|---|
| **SHA-256 Hashing** | `hashlib.sha256()` — one-way hash function applied to each password candidate |
| **Dictionary Attack Simulation** | Wordlist is pre-processed into a hash dictionary; each user hash is looked up in O(1) — mirrors the logic of real-world offline credential auditing |
| **JSON I/O** | `json.load()` / `json.dump()` — structured data in, structured report out |
| **Error Handling** | `try/except` for `FileNotFoundError` and `JSONDecodeError` — graceful failure |
| **Modular Design** | Single-responsibility functions — each does one job only |
| **Encoding Awareness** | `utf-8` encoding specified on all file reads — prevents charset errors on Windows |
| **None-safe Comparison** | `if matched_password is not None` — avoids missed detections on empty-string passwords |

---

## ⚡ Algorithmic Design: O(1) Lookup with Internal Plaintext Matching

A naive implementation would use a linear search — for every user hash, iterate through the entire wordlist. That results in O(n × m) time complexity, where n = number of users and m = wordlist size. With `rockyou.txt` at 14 million entries, this bottlenecks at scale.

**This project implements an efficient O(1) lookup approach** — the wordlist is pre-processed into a Python dictionary where each key is a SHA-256 hash and each value is the wordlist entry, held in memory for match detection only:

```python
# O(1) lookup — implemented in build_hash_dict()
common_hash_dict = {hash_password(p): p for p in common_passwords}

# Lookup is instant regardless of wordlist size
matched_password = common_hash_dict.get(stored_hash)
```

This achieves O(1) lookup speed and allows the tool to confirm whether a stored hash corresponds to a known weak password without exposing plaintext passwords in the audit output. A plain `set` would give speed but lose the ability to distinguish which wordlist entry matched; a `dict` enables both detection and risk categorisation.

---

## 💡 Security Insights

**Why SHA-256 alone is not safe for password storage:**

SHA-256 is a *fast* hashing algorithm — designed for checksums and data integrity. Speed is a feature for those use cases but a critical vulnerability for passwords. An attacker with a modern GPU can compute **billions of SHA-256 hashes per second**, making dictionary and brute-force attacks highly effective.

**The missing layer — salting:**

A cryptographic salt is a random value added to each password before hashing, producing a unique hash even for identical passwords. Without salting, two users with the password `password123` produce the same hash — making bulk cracking trivial.

```
Without salt:  SHA256("password123")           → ef92b778...  ← identical for every user
With salt:     SHA256("password123" + "x7kQ9z") → fa8ae954...  ← unique per user
```

**What organisations should use instead:**

| Algorithm | Why It's Better |
|---|---|
| **bcrypt** | Deliberately slow; has a configurable cost factor that can be increased as hardware gets faster |
| **Argon2** | Winner of the Password Hashing Competition; GPU-resistant |
| **PBKDF2** | NIST-recommended; configurable iteration count |

This project intentionally uses SHA-256 to demonstrate the vulnerability — not as a recommendation for production systems.

---

## 📁 Project Structure

```
Cybersecurity-Password-Audit/
│
├── password_audit.py          ← Main audit script
├── user_data.json             ← Mock user database (synthetic data only)
├── output.json                ← Sample audit results (regenerated on each run)
├── rockyou_sample.txt         ← Sample wordlist (1,000 entries for demo)
├── .gitignore                 ← Excludes rockyou.txt and cache files
│
└── README.md                  ← Project documentation (you are here)
```

> **Note:** The full `rockyou.txt` (14M+ passwords) is NOT included. Download it from [SecLists on GitHub](https://github.com/danielmiessler/SecLists) for local testing.

---

## ⚙️ Setup & Usage

**Requirements:**
- Python 3.6 or higher
- No external libraries — uses Python standard library only (`hashlib`, `json`, `os`)

```bash
# 1. Clone the repository
git clone https://github.com/Lucas-GCamargo/Cybersecurity-Password-Audit

# 2. Navigate into the folder
cd Cybersecurity-Password-Audit

# 3. Add rockyou.txt to the project folder
#    (or use the included rockyou_sample.txt for demo purposes)

# 4. Run the script
# On Linux / macOS:
python3 password_audit.py

# On Windows:
python password_audit.py
```

**Expected terminal output:**
```
============================================================
  Cybersecurity Password Audit Tool
  Author: Lucas Camargo
============================================================

[✔] Loaded 10 user record(s) from 'user_data.json'.
[!] 'rockyou.txt' not found. Falling back to 'rockyou_sample.txt'.
[✔] Loaded 1,000 passwords from wordlist.

[*] Building hash dictionary from wordlist...
[✔] Hash dictionary ready — 994 unique entries indexed.

[*] Running password audit...


[!] Audit complete — 7 of 10 account(s) flagged as vulnerable.
[✔] Results saved to 'output.json'.

[i] Run with --interactive flag to enter manual hashing mode.
```

> To enable interactive hashing mode: `python3 password_audit.py --interactive`

> **Note:** The dictionary shows 994 entries (not 1,000) because 6 passwords appear twice in the wordlist file (`qwerty123`, `trustno1`, `parrot12`, `hydra123`, `medusa12`, `cortex12`). The dictionary deduplicates them automatically, keeping only one entry per unique password. SHA-256 has no known hash collisions — the deduplication is on the plaintext, not the hash.

---

## 📊 Sample Output (output.json)

```json
[
    {
        "username": "jsmith",
        "hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",
        "password_cracked": true,
        "risk": "weak_dictionary_password_detected"
    },
    {
        "username": "ajonas",
        "hash": "a3f1f9e2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0",
        "password_cracked": false,
        "risk": "not_found_in_wordlist"
    }
]
```

Accounts where `"password_cracked": true` have hashes matching a known common password and should be immediately flagged for a mandatory password reset. **Plaintext passwords are never stored in the output** — only the original hash, cracked status, and risk category. This follows security audit best practices.

---

## 🧠 What I Learned

**1. How dictionary attacks actually work — and how defenders think about them**
Building the wordlist pre-processing step from scratch made the mechanics of offline credential attacks concrete. A real attacker hashes millions of common passwords and compares them against a stolen database. This tool simulates the same logic from the defender's side — and then goes further by replacing the naive O(n × m) iteration with a pre-computed hash dictionary, so lookups are O(1) regardless of wordlist size.

**2. Why fast hashing is the wrong choice for passwords**
SHA-256's speed, which makes it excellent for file integrity checks, becomes a liability for password storage. Researching bcrypt and Argon2 deepened my understanding of why the cryptographic community moved away from general-purpose hash functions for credentials.

**3. The importance of salting**
Discovering that two identical passwords produce the same SHA-256 hash — and understanding the implications for bulk cracking — made the purpose of per-user salts immediately clear.

**4. Algorithmic design matters in security tooling**
Switching from a linear search to a pre-computed hash dictionary reduced the lookup complexity from O(n × m) to O(1), while also enabling risk categorisation in the output. A `set` would only confirm presence; a `dict` enables detection plus category labelling — without storing plaintext in the report.

---

## ⚠️ Limitations

**1. No salting support**
The current script compares unsalted hashes only. Real-world databases use per-user salts, making this approach ineffective without first extracting the salt for each account.

**2. Single hash algorithm — SHA-256 only**
The script only recognises SHA-256 formatted hashes. Real-world database dumps may use MD5, NTLM, or other unsalted hash formats that could be audited with a similar approach. Purpose-built password hashing algorithms such as bcrypt and Argon2 embed a unique per-user salt inside the hash itself, making dictionary attacks fundamentally incompatible — not just unsupported by this tool.

**3. Single-threaded**
The audit runs on a single thread. For very large user databases, a multi-threaded or multiprocessing approach would improve performance.

---

## 🔗 References

- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [NIST SP 800-63B — Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [Australian Cyber Security Centre](https://www.cyber.gov.au)
- [SecLists — rockyou.txt](https://github.com/danielmiessler/SecLists)

---

## 🤝 Let's Connect

I am a cybersecurity analyst with hands-on experience in Python scripting, ethical hacking fundamentals, and defensive security tooling.

- 📧 [lucascamargo@outlook.com.au](mailto:lucascamargo@outlook.com.au)
- 🔗 [linkedin.com/in/lucasgcamargo](https://www.linkedin.com/in/lucasgcamargo/)

---

## © Copyright

© 2026 Lucas Camargo. All Rights Reserved.
This project is for educational and portfolio purposes. The author accepts no responsibility for misuse.
