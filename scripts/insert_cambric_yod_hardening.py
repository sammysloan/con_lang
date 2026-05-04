"""
Insert Cambric evolution preset – Word-initial yod hardening (rule 61).
Run from project root: python3 scripts/insert_cambric_yod_hardening.py

Word-initial /j/ gains a velar onset → /ɡj/, parallel to Rule 60 (w→ɡw).
Both glides harden at word boundary: the same mechanism, different place.
Orthographic output: <gy-> (e.g. *yowankos → gyúanc).
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

RULES = [
    (61, {
        "name": "Word-initial j → ɡj",
        "type": "syll",
        "notes": "Word-initial /j/ gains a velar onset, producing /ɡj/. Parallel to Rule 60 (w→ɡw): both glides harden at word boundary via the same mechanism. Orthographically <gy->, hinting at the vestigial palatal glide. Cf. Welsh initial mutations and Irish <gi-> clusters.",
        "old_list": ["j"],
        "new_list": ["ɡj"],
        "position": "first",
        "pre_list": ["*Blank"],
        "post_list": [],
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
        print(f"Removed {cur.rowcount} existing rule(s) at order(s) {orders}.")

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
