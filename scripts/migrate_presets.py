"""
Migration: per-table preset schema → single 'presets' table

Old schema: one table per preset, each with (id, rule TEXT) columns
New schema: one 'presets' table with (id, preset_name, rule_order, rule) columns

Run once from the project root:
    python scripts/migrate_presets.py
"""
import os
import shutil
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "presets", "presets.db")

SKIP_TABLES = {"sqlite_sequence", "orth_presets", "presets"}


def migrate():
    if not os.path.exists(DB_PATH):
        print(f"[Error] Database not found: {DB_PATH}")
        return

    # Backup before touching anything
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH + f".backup_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup created: {backup_path}")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Find all preset tables (exclude system and non-preset tables)
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """)
        all_tables = [row[0] for row in cursor.fetchall()]
        preset_tables = [t for t in all_tables if t not in SKIP_TABLES]

        if not preset_tables:
            print("No preset tables found to migrate.")
            return

        print(f"Found {len(preset_tables)} preset(s): {preset_tables}")

        # Create new unified table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS presets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                preset_name TEXT NOT NULL,
                rule_order  INTEGER NOT NULL,
                rule        TEXT NOT NULL
            )
        """)

        # Migrate each preset table
        for table in preset_tables:
            cursor.execute(f'SELECT id, rule FROM "{table}" ORDER BY id')
            rows = cursor.fetchall()
            for order, (_, rule) in enumerate(rows):
                cursor.execute(
                    "INSERT INTO presets (preset_name, rule_order, rule) VALUES (?, ?, ?)",
                    (table, order, rule)
                )
            print(f"  Migrated {len(rows)} rule(s) from '{table}'")

        # Drop old preset tables
        for table in preset_tables:
            cursor.execute(f'DROP TABLE "{table}"')
            print(f"  Dropped old table '{table}'")

        conn.commit()

    print("Migration complete. Your presets are preserved in the new schema.")
    print(f"Original backed up to: {backup_path}")


if __name__ == "__main__":
    migrate()
