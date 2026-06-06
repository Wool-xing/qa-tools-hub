#!/usr/bin/env python3
"""QA通关 database backup and restore utility.

Usage:
    python scripts/backup.py backup              # Create timestamped backup
    python scripts/backup.py list                # List available backups
    python scripts/backup.py restore <filename>  # Restore from backup
"""

import os
import sys
import shutil
import glob
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "qa_tools.db")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "backups")
KEEP_LAST = int(os.getenv("BACKUP_KEEP_LAST", "14"))


def _ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def backup():
    if not os.path.isfile(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        sys.exit(1)

    _ensure_backup_dir()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"qa_tools_{ts}.db")
    shutil.copy2(DB_PATH, dest)
    print(f"Backup: {dest} ({os.path.getsize(dest)} bytes)")

    # Rotate old backups
    files = sorted(glob.glob(os.path.join(BACKUP_DIR, "qa_tools_*.db")))
    for old in files[:-KEEP_LAST]:
        os.unlink(old)
        print(f"Rotated: {old}")


def list_backups():
    _ensure_backup_dir()
    files = sorted(glob.glob(os.path.join(BACKUP_DIR, "qa_tools_*.db")), reverse=True)
    if not files:
        print("No backups found.")
        return
    for f in files:
        sz = os.path.getsize(f)
        print(f"{os.path.basename(f)}  ({sz:,} bytes)")


def restore(filename):
    src = os.path.join(BACKUP_DIR, filename)
    # Prevent path traversal
    real_src = os.path.realpath(src)
    real_dir = os.path.realpath(BACKUP_DIR)
    if not real_src.startswith(real_dir + os.sep):
        print(f"Invalid backup filename: {filename}")
        sys.exit(1)
    if not os.path.isfile(src):
        print(f"Backup not found: {src}")
        sys.exit(1)

    if os.path.isfile(DB_PATH):
        # Keep a safety copy before overwriting
        safety = DB_PATH + ".pre-restore"
        shutil.copy2(DB_PATH, safety)
        print(f"Safety copy: {safety}")

    shutil.copy2(src, DB_PATH)
    print(f"Restored: {src} → {DB_PATH}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "backup":
        backup()
    elif cmd == "list":
        list_backups()
    elif cmd == "restore" and len(sys.argv) > 2:
        restore(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
