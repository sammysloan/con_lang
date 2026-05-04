"""
Migration: convert stored rule JSON from positional-list format to named-dict format.

Run once from the project root:
    python scripts/migrate_rules_to_dict.py
"""
import json
import os
import shutil
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "presets", "presets.db")


def list_to_dict(raw: list) -> dict:
    name, rule_type, notes = raw[0], raw[1], raw[2]
    p = raw[3:]
    base = {"name": name, "type": rule_type, "notes": notes}

    if rule_type == "ass":
        base.update({"targets": p[0], "triggers": p[1], "replace": p[2],
                     "regressive": p[3],
                     "skip_stress": p[4] if len(p) > 4 else False,
                     "require_identical": p[5] if len(p) > 5 else False})

    elif rule_type == "disc":
        # Fix: old UI put require_identical at p[6]; evolver wrongly read index 11
        base.update({"targets": p[0], "triggers": p[1], "replace": p[2],
                     "regressive": p[3],
                     "skip_stress": p[4] if len(p) > 4 else False,
                     "max_distance": p[5] if len(p) > 5 else 3,
                     "require_identical": p[6] if len(p) > 6 else False})

    elif rule_type == "clp":
        base.update({"position": p[0], "scope": p[1],
                     "allow": p[2] if len(p) > 2 else [],
                     "ban":   p[3] if len(p) > 3 else [],
                     "max_check": p[4] if len(p) > 4 else 3})

    elif rule_type == "con":
        base.update({"old_list": p[0], "new_list": p[1],
                     "pre_trig":  p[2] if len(p) > 2 else [],
                     "post_trig": p[3] if len(p) > 3 else [],
                     "pre_ex":    p[4] if len(p) > 4 else [],
                     "post_ex":   p[5] if len(p) > 5 else [],
                     "skip_stress": p[6] if len(p) > 6 else False,
                     "stress_solo": p[7] if len(p) > 7 else False})

    elif rule_type == "del":
        base.update({"del_list": p[0],
                     "pre_list":    p[1] if len(p) > 1 else [],
                     "post_list":   p[2] if len(p) > 2 else [],
                     "except_pre":  p[3] if len(p) > 3 else [],
                     "except_post": p[4] if len(p) > 4 else [],
                     "skip_stress":   p[5] if len(p) > 5 else False,
                     "stress_solo":   p[6] if len(p) > 6 else False,
                     "sonority_safe": p[7] if len(p) > 7 else True})

    elif rule_type == "epen":
        base.update({"find_list": p[0], "replace_list": p[1],
                     "syllable_pos": p[2],
                     "pre_list":  p[3] if len(p) > 3 else [],
                     "post_list": p[4] if len(p) > 4 else []})

    elif rule_type == "str":
        base["mode"] = p[0]
        if p[0] == "weight":
            base.update({"weight_default": p[1] if len(p) > 1 else "penult",
                         "weight_window":  p[2] if len(p) > 2 else 3,
                         "coda_matters":   p[3] if len(p) > 3 else True,
                         "skip_ultimate":  p[4] if len(p) > 4 else False})

    elif rule_type == "syll":
        base.update({"old_list": p[0], "new_list": p[1], "position": p[2],
                     "pre_list":   p[3] if len(p) > 3 else [],
                     "post_list":  p[4] if len(p) > 4 else [],
                     "skip_stress": p[5] if len(p) > 5 else False,
                     "stress_solo": p[6] if len(p) > 6 else False})

    else:
        raise ValueError(f"Unknown rule type: {rule_type!r}")

    return base


def migrate():
    if not os.path.exists(DB_PATH):
        print(f"[Error] Database not found: {DB_PATH}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH + f".backup_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup created: {backup_path}")

    converted = skipped = errors = 0

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, preset_name, rule FROM presets ORDER BY preset_name, rule_order")
        rows = cursor.fetchall()

        for row_id, preset_name, rule_json in rows:
            try:
                data = json.loads(rule_json)
            except json.JSONDecodeError as e:
                print(f"  [Error] Could not parse rule id={row_id}: {e}")
                errors += 1
                continue

            if isinstance(data, dict):
                skipped += 1
                continue  # already a dict, nothing to do

            if not isinstance(data, list):
                print(f"  [Warning] Unexpected type for rule id={row_id}: {type(data)}")
                errors += 1
                continue

            try:
                new_data = list_to_dict(data)
            except Exception as e:
                print(f"  [Error] Could not convert rule id={row_id} in '{preset_name}': {e}")
                errors += 1
                continue

            cursor.execute("UPDATE presets SET rule = ? WHERE id = ?",
                           (json.dumps(new_data, ensure_ascii=False), row_id))
            converted += 1

        conn.commit()

    print(f"\nDone. Converted: {converted}  Already dict: {skipped}  Errors: {errors}")
    print(f"Original backed up to: {backup_path}")


if __name__ == "__main__":
    migrate()
