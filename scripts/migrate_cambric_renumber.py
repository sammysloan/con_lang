"""
Renumber all Cambric rules ×10 (giving room between orders),
then insert the P-Celtic shift at order 5.

Run from project root: python3 scripts/migrate_cambric_renumber.py
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

P_CELTIC_SHIFT = {
    "name": "P-Celtic shift",
    "type": "con",
    "notes": "P-Celtic: *kʷ → p and *ɡʷ → b. Marks the Brittonic/Goidelic split. Cf. Welsh pedwar vs Irish ceathair (four), Welsh pen vs Irish ceann (head).",
    "old_list": ["kʷ", "ɡʷ"],
    "new_list": ["p", "b"],
    "pre_trig": [], "post_trig": [], "pre_ex": [], "post_ex": [],
    "skip_stress": False, "stress_solo": False,
}

def main():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Fetch current rules in order
    cur.execute(
        "SELECT id, rule_order, rule FROM presets WHERE preset_name=? ORDER BY rule_order",
        (PRESET,)
    )
    rows = cur.fetchall()
    if not rows:
        print(f"No rules found for preset '{PRESET}'. Nothing to do.")
        conn.close()
        return

    print(f"Found {len(rows)} existing rules. Renumbering ×10...")
    # Update in reverse order to avoid collisions if any order already exists ×10
    for row_id, old_order, rule_json in reversed(rows):
        new_order = old_order * 10
        cur.execute(
            "UPDATE presets SET rule_order=? WHERE id=?",
            (new_order, row_id)
        )
        print(f"  {old_order:>3} → {new_order:>4}  ({json.loads(rule_json)['name']})")

    # Insert P-Celtic shift at order 5
    cur.execute(
        "INSERT INTO presets (preset_name, rule_order, rule) VALUES (?, ?, ?)",
        (PRESET, 5, json.dumps(P_CELTIC_SHIFT, ensure_ascii=False))
    )
    print(f"\n  Inserted at order 5: {P_CELTIC_SHIFT['name']}")

    conn.commit()
    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
