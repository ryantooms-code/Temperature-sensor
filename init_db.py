"""
init_db.py - One-shot script to create sense_data.db and its schema.
Run this once before starting the app, or whenever you need to reset the DB.

Usage:
    python init_db.py
"""

import os
import sys

# Allow running from the project root without installing the package
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, DB_PATH

if __name__ == "__main__":
    print(f"Initialising database at: {DB_PATH}")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    init_db()
    print("Done — sense_data.db is ready.")
