"""
Insert Cambric evolution preset – Schwa-conditioned stop voicing (rule 133).
Run from project root: python3 scripts/insert_cambric_schwa_voicing.py

Word-final voiceless stops voice to their voiced counterparts after schwa:
p→b, t→d, k→g / ə _ #

This is the Brythonic soft-mutation pattern (p→b, t→d, c→g) expressed as a
phonological rule: the weakest vowel environment (schwa) triggers the mildest
lenition (simple voicing). Contrasts with Rule 130, which spirantizes the same
stops to voiceless fricatives after full vowels.
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

RULES = [
    (133, {
        "name": "Schwa-conditioned stop voicing",
        "type": "syll",
        "notes": "Word-final voiceless stops voice after schwa: p→b, t→d, k→g / ə_#. Schwa, as the weakest vowel, triggers only the first stage of Brythonic lenition (simple voicing) rather than the full spirantization that full vowels produce (Rule 130). Reflects the Welsh soft-mutation pattern (p→b, t→d, c→g) as a phonological rather than morphological process.",
        "old_list": ["p", "t", "k"],
        "new_list": ["b", "d", "g"],
        "position": "last",
        "pre_list": ["ə"],
        "post_list": ["*Blank"],
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
