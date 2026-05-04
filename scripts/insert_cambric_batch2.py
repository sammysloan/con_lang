"""
Insert Cambric evolution preset – Batch 2 (rules 5–9).
Run from project root: python3 scripts/insert_cambric_batch2.py
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

# Vowels present in Cambric at this stage (for intervocalic context triggers)
V = ["au", "ai", "ei", "oi", "ou", "a", "e", "i", "o", "u",
     "aː", "eː", "iː", "oː", "uː"]

RULES = [
    (5, {
        "name": "ɸ → f",
        "type": "con",
        "notes": "Proto-Celtic bilabial fricative /ɸ/ (< IE *p, preserved in clusters) normalises to /f/. Cf. Welsh ffon < *ɸonā.",
        "old_list": ["ɸ"],
        "new_list": ["f"],
        "pre_trig": [], "post_trig": [], "pre_ex": [], "post_ex": [],
        "skip_stress": False, "stress_solo": False,
    }),
    (6, {
        "name": "Word-initial w → ɡw",
        "type": "syll",
        "notes": "Brittonic - Word-initial /w/ gains velar onset, cf. Welsh gwin, gwir, gwaed. Parallel to Marcher /v/→/ɡw/ but from Celtic /w/ not Latin /w/.",
        "old_list": ["w"],
        "new_list": ["ɡw"],
        "position": "first",
        "pre_list": ["*Blank"], "post_list": [],
        "skip_stress": False, "stress_solo": False,
    }),
    (7, {
        "name": "Intervocalic lenition: voiceless stops",
        "type": "con",
        "notes": "Gaelic-style spirantisation of intervocalic voiceless stops: p→f, t→θ, k→x. Fires on the post-apocope forms so word-final stops are unaffected.",
        "old_list": ["p", "t", "k"],
        "new_list": ["f", "θ", "x"],
        "pre_trig": V, "post_trig": V,
        "pre_ex": [], "post_ex": [],
        "skip_stress": False, "stress_solo": False,
    }),
    (8, {
        "name": "Intervocalic lenition: voiced stops",
        "type": "con",
        "notes": "Pan-Celtic spirantisation of intervocalic voiced stops: b→v, d→ð, g→ɣ. Cf. Welsh byw, Middle Welsh dydd, Old Irish gáu.",
        "old_list": ["b", "d", "ɡ"],
        "new_list": ["v", "ð", "ɣ"],
        "pre_trig": V, "post_trig": V,
        "pre_ex": [], "post_ex": [],
        "skip_stress": False, "stress_solo": False,
    }),
    (9, {
        "name": "Intervocalic ɣ deletion",
        "type": "del",
        "notes": "Intervocalic /ɣ/ (< lenited /g/) is unstable and deleted, as in Irish and many Brittonic dialects. /ð/ and /v/ are retained.",
        "del_list": ["ɣ"],
        "pre_list": V, "post_list": V,
        "except_pre": [], "except_post": [],
        "skip_stress": False, "stress_solo": False,
        "sonority_safe": False,
    }),
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Remove only batch-2 orders (idempotent)
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
    print(f"\nDone. {len(RULES)} rules inserted into preset '{PRESET}'.")

if __name__ == "__main__":
    main()
