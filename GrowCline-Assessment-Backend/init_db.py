"""
Database Initialization Script
Connects to MongoDB Atlas and explicitly creates required collections.
"""

import sys
import os
import io

# Ensure stdout can handle UTF-8 / emojis on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure the app root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.config.database import Database

def main():
    print("[INIT] Initializing MongoDB Atlas Database & Collections...")
    try:
        db = Database.connect()
        collections = db.list_collection_names()
        print("\n[SUCCESS] Initialization Complete!")
        print(f"[*] Active Database: {db.name}")
        print(f"[*] Collections in MongoDB Atlas: {collections}")
    except Exception as error:
        print(f"\n[ERROR] Initialization failed: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()
