"""
Insert Cambric evolution preset – Batch 1 (rules 0–4).
Run from project root: python scripts/insert_cambric_batch1.py
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

RULES = [
    (0, {
        "name": "Initial stress",
        "type": "str",
        "notes": "Gaelic-style - Stress shifts to word-initial position, diverging from Welsh penultimate stress. Shared convergent feature with Marcher.",
        "mode": "first",
    }),
    (1, {
        "name": "Brittonic long vowel shift",
        "type": "con",
        "notes": "Proto-Brittonic vowel raising: *ā > ō, *ō > ū, *ē > ī. Universal Brittonic change, cf. Welsh tad < *tātā, du < *dūbos.",
        "old_list": ["aː", "oː", "eː"],
        "new_list": ["oː", "uː", "iː"],
        "pre_trig": [], "post_trig": [], "pre_ex": [], "post_ex": [],
        "skip_stress": False, "stress_solo": False,
    }),
    (2, {
        "name": "Loss of final -s, -n, -m",
        "type": "syll",
        "notes": "Proto-Brittonic loss of nominative -s, accusative -n, and neuter -m endings. syll/last scope ensures *Blank = true word-end. Cf. Welsh mawr < *māros, llawn < *lānon.",
        "old_list": ["s", "n", "m"],
        "new_list": ["", "", ""],
        "position": "last",
        "pre_list": [], "post_list": ["*Blank"],
        "skip_stress": False, "stress_solo": False,
    }),
    (3, {
        "name": "Apocope",
        "type": "syll",
        "notes": "Loss of final unstressed vowel (short or long). Long final vowels arise from ā-stem feminines (*-ā > -oː via Rule 1) and must also be deleted. syll/last scope prevents firing on mid-word syllable-boundary vowels.",
        "old_list": ["a", "e", "i", "o", "u", "oː", "uː", "iː"],
        "new_list": ["", "", "", "", "", "", "", ""],
        "position": "last",
        "pre_list": [], "post_list": ["*Blank"],
        "skip_stress": True, "stress_solo": False,
    }),
    (4, {
        "name": "Degemination",
        "type": "ass",
        "notes": "Reduction of geminate consonants to singletons. Cf. Welsh cath < *cattā, nos < *noktis.",
        "targets":  ["p","t","k","b","d","ɡ","m","n","l","r","s","ɸ","w"],
        "triggers": ["p","t","k","b","d","ɡ","m","n","l","r","s","ɸ","w"],
        "replace":  ["", "", "", "", "", "", "", "", "", "", "", "", ""],
        "regressive": True, "skip_stress": False, "require_identical": True,
    }),
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Wipe any previous Cambric rules (idempotent re-runs)
    cur.execute("DELETE FROM presets WHERE preset_name = ?", (PRESET,))
    deleted = cur.rowcount
    if deleted:
        print(f"Removed {deleted} existing Cambric rule(s).")

    for order, rule_dict in RULES:
        cur.execute(
            "INSERT INTO presets (preset_name, rule_order, rule) VALUES (?, ?, ?)",
            (PRESET, order, json.dumps(rule_dict, ensure_ascii=False)),
        )
        print(f"  Inserted rule {order}: {rule_dict['name']}")

    conn.commit()
    conn.close()
    print(f"\nDone. {len(RULES)} rules inserted into preset '{PRESET}'.")

if __name__ == "__main__":
    main()
