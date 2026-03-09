"""
password_audit.py
-----------------
Cybersecurity Password Audit Tool
Author: Lucas Camargo
Course: TAFE Cybersecurity Program
Year:   2026

ETHICAL USE NOTICE:
This tool is for educational and authorised auditing purposes only.
Running this tool against systems you do not own or have explicit
written permission to audit is illegal under the Australian Criminal
Code Act 1995 (Cth) — s477.1.
"""

import hashlib
import json
import os


# ── 1. Load user database ────────────────────────────────────────────────────

def load_user_data(filepath="user_data.json"):
    """Load and return the list of user records from a JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"[✘] Error: '{filepath}' must contain a JSON array [ ], not an object {{ }}.")
            return []
        print(f"[✔] Loaded {len(data)} user record(s) from '{filepath}'.")
        return data
    except FileNotFoundError:
        print(f"[✘] Error: '{filepath}' not found. Please check the file path.")
        return []
    except json.JSONDecodeError:
        print(f"[✘] Error: '{filepath}' contains invalid JSON.")
        return []


# ── 2. Load wordlist ─────────────────────────────────────────────────────────

def load_common_passwords(filepath="rockyou.txt"):
    """Load common passwords from a wordlist file. Falls back to sample file."""
    if not os.path.exists(filepath):
        fallback = "rockyou_sample.txt"
        print(f"[!] '{filepath}' not found. Falling back to '{fallback}'.")
        filepath = fallback

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            passwords = [line.strip() for line in f if line.strip()]
        print(f"[✔] Loaded {len(passwords):,} passwords from wordlist.")
        return passwords
    except FileNotFoundError:
        print(f"[✘] Error: No wordlist file found. Place 'rockyou.txt' or 'rockyou_sample.txt' in the project folder.")
        return []


# ── 3. Hash a single password ────────────────────────────────────────────────

def hash_password(password):
    """Return the SHA-256 hex digest of a given password string."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ── 4. Build hash dictionary and retrieve compromised passwords ───────────────

def build_hash_dict(common_passwords):
    """
    Pre-compute SHA-256 hashes for all wordlist entries into a dictionary.
    Key   = SHA-256 hash of the password
    Value = Original plaintext password

    Using a dictionary (instead of a set) allows O(1) lookup speed while
    also preserving the plaintext password so it can be included in the report.
    """
    return {hash_password(p): p for p in common_passwords}


def get_compromised_password(user_hash, common_hash_dict):
    """
    Return the plaintext password if the hash exists in the dictionary.
    Returns None if no match is found.

    Kept as a named function (rather than an inline .get() call) to make
    check_passwords() self-documenting and to allow future extension —
    e.g. adding confidence scoring, logging matched hashes, or supporting
    multiple hash format lookups.
    """
    return common_hash_dict.get(user_hash)


# ── 5. Audit all user accounts ───────────────────────────────────────────────

def check_passwords(user_data, common_hash_dict):
    """
    Compare each user's stored hash against the wordlist hash dictionary.
    Returns a list of result dictionaries including the matched plaintext password.
    """
    results = []
    vulnerable_count = 0
    processed_count = 0

    for user in user_data:
        # Guard against malformed records (non-dict entries in the JSON array)
        if not isinstance(user, dict):
            print(f"[!] Warning: Skipping malformed record — expected dict, got {type(user).__name__}.")
            continue

        processed_count += 1
        username = user.get("username", "unknown")
        stored_hash = user.get("user_password", "")

        matched_password = get_compromised_password(stored_hash, common_hash_dict)

        # NOTE: Must check 'is not None' (not just truthiness) because an empty
        # string password "" would evaluate as False and cause a missed detection.
        if matched_password is not None:
            vulnerable_count += 1
            found = True
        else:
            matched_password = ""
            found = False

        results.append({
            "username": username,
            "password": matched_password,
            "password_found": found
        })

    print(f"\n[!] Audit complete — {vulnerable_count} of {processed_count} account(s) flagged as vulnerable.")
    return results


# ── 6. Save results to JSON ───────────────────────────────────────────────────

def save_results(results, filepath="output.json"):
    """Write the audit results to a JSON output file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        print(f"[✔] Results saved to '{filepath}'.")
    except IOError as e:
        print(f"[✘] Failed to write results: {e}")


# ── 7. Interactive hashing mode ───────────────────────────────────────────────

def interactive_mode():
    """Allow the user to hash arbitrary strings manually for verification."""
    print("\n─── Interactive Hashing Mode ───────────────────────────────")
    print("Type any string to see its SHA-256 hash. Type 'exit' to quit.\n")
    while True:
        try:
            user_input = input("Enter a string to hash (or 'exit'): ").strip()
        except (KeyboardInterrupt, EOFError):
            # Graceful exit if user presses Ctrl+C or input is piped/automated
            print("\nExiting interactive mode.")
            break
        if user_input.lower() == "exit":
            print("Exiting interactive mode.")
            break
        if not user_input:
            print("  [!] Please enter a non-empty string.\n")
            continue
        result = hash_password(user_input)
        print(f"  SHA-256 → {result}\n")


# ── 8. Entry point ────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Cybersecurity Password Audit Tool")
    print("  Author: Lucas Camargo | TAFE Cybersecurity 2026")
    print("=" * 60 + "\n")

    # Load user database
    user_data = load_user_data("user_data.json")
    if not user_data:
        return

    # Load wordlist
    common_passwords = load_common_passwords("rockyou.txt")
    if not common_passwords:
        return

    # Build hash dictionary — O(1) lookups with plaintext recovery
    print("\n[*] Building hash dictionary from wordlist...")
    common_hash_dict = build_hash_dict(common_passwords)
    print(f"[✔] Hash dictionary ready — {len(common_hash_dict):,} unique entries indexed.")

    # Run audit
    print("\n[*] Running password audit...\n")
    results = check_passwords(user_data, common_hash_dict)

    # Save report
    save_results(results, "output.json")

    # Interactive mode
    interactive_mode()


if __name__ == "__main__":
    main()
