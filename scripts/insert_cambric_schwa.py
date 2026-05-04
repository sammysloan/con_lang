"""
Insert Cambric evolution preset – Schwa rule (rule 118).
Run from project root: python3 scripts/insert_cambric_schwa.py

Slots between unstressed long vowel shortening (115) and ɨ deletion (120).
ɨ → ə when followed by a consonant: preserves reduced vowels structurally
rather than deleting them, producing Welsh-style schwa in polysyllabic words.
Word-final ɨ (not followed by a consonant) is unaffected and still deleted by 120.
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

RULES = [
    (118, {
        "name": "ɨ → ə before consonant",
        "type": "con",
        "notes": "Reduced /ɨ/ surfaces as schwa /ə/ rather than being deleted when followed by a consonant. The vowel is preserved where it has structural work to do — supporting a coda or bridging a cluster. Word-final ɨ (no following consonant) is left for Rule 120 to delete. Cf. Welsh unstressed /ə/ in polysyllabic words.",
        "old_list": ["ɨ"],
        "new_list": ["ə"],
        "pre_trig": [],
        "post_trig": ["*Consonants"],
        "pre_ex": [],
        "post_ex": [],
        "skip_stress": False,
        "stress_solo": False,
    }),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    orders = [r[0] for r in RULES]
    placeholders = ",".join("?" * len(orders))
    cur.execute(
        f"DELETE FROM presets WHERE preset_name=? AND rule_order IN ({placeholders})",
        [PRESET] + orders,
    )
    if cur.rowcount:
        print(f"Removed {cur.rowcount} existing rule(s) at orders {orders}.")

    for order, rule_dict in RULES:
        cur.execute(
            "INSERT INTO presets (preset_name, rule_order, rule) VALUES (?, ?, ?)",
            (PRESET, order, json.dumps(rule_dict, ensure_ascii=False)),
        )
        print(f"  Inserted rule {order}: {rule_dict['name']}")

    conn.commit()
    conn.close()
    print(f"\nDone. {len(RULES)} rule(s) inserted into preset '{PRESET}'.")


if __name__ == "__main__":
    main()
