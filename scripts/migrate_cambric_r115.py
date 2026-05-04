"""
Move Cambric Rule 115 (unstressed long vowel shortening) from order 115 to order 108.

The rule must fire BEFORE Rule 110 (short vowel reduction, order 110) so that
back/open long vowels (oː→o, uː→u, aː→a) are then caught by Rule 110 and
reduced to ɨ → deleted/schwa. Front long vowels (iː→i, eː→e) still survive
since /i/ and /e/ are not in Rule 110's target set — matching Welsh behaviour.

Run from project root: python3 scripts/migrate_cambric_r115.py
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

OLD_ORDER = 115
NEW_ORDER = 108


def main():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    cur.execute(
        "SELECT rule FROM presets WHERE preset_name=? AND rule_order=?",
        (PRESET, OLD_ORDER),
    )
    row = cur.fetchone()
    if not row:
        print(f"No rule found at order {OLD_ORDER} for preset '{PRESET}'. Nothing to do.")
        conn.close()
        return

    rule_json = row[0]
    rule = json.loads(rule_json)
    print(f"Found rule at order {OLD_ORDER}: {rule['name']}")

    # Remove from old position
    cur.execute(
        "DELETE FROM presets WHERE preset_name=? AND rule_order=?",
        (PRESET, OLD_ORDER),
    )

    # Clear any existing rule at the target order
    cur.execute(
        "DELETE FROM presets WHERE preset_name=? AND rule_order=?",
        (PRESET, NEW_ORDER),
    )

    # Insert at new position
    cur.execute(
        "INSERT INTO presets (preset_name, rule_order, rule) VALUES (?, ?, ?)",
        (PRESET, NEW_ORDER, rule_json),
    )

    conn.commit()
    conn.close()
    print(f"Moved '{rule['name']}' from order {OLD_ORDER} → order {NEW_ORDER}.")
    print("Unstressed long back/open vowels (oː, uː, aː) will now be reduced to ɨ")
    print("and deleted/schwa. Front long vowels (iː, eː) survive as short i/e.")


if __name__ == "__main__":
    main()
