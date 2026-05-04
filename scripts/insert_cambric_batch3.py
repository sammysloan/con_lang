"""
Insert Cambric evolution preset – Batch 3 (rules 100–120).
Run from project root: python3 scripts/insert_cambric_batch3.py
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

RULES = [
    (100, {
        "name": "Diphthong monophthongization",
        "type": "con",
        "notes": "Gaelic-style collapse of diphthongs: au→oː, ou→uː, ei→iː, oi→oː, ai→eː. Cf. Irish ór < *auros, úr < *ouros.",
        "old_list": ["au", "ou", "ei", "oi", "ai"],
        "new_list": ["oː", "uː", "iː", "oː", "eː"],
        "pre_trig": [], "post_trig": [], "pre_ex": [], "post_ex": [],
        "skip_stress": False, "stress_solo": False,
    }),
    (105, {
        "name": "I-affection",
        "type": "disc",
        "notes": "Brittonic i-affection (umlaut): stressed back/open vowels front when /i/ or /iː/ follows in a later syllable. a→e, o→e, u→i. Runs before reduction so the /i/ trigger is still present.",
        "targets":  ["a", "o", "u"],
        "triggers": ["i", "iː", "j"],
        "replace":  ["e", "e", "i"],
        "regressive": True,
        "max_distance": 4,
        "skip_stress": False,
        "require_identical": False,
    }),
    (110, {
        "name": "Unstressed short vowel reduction",
        "type": "con",
        "notes": "Unstressed back/open vowels (a, o, u) collapse to /ɨ/. High front vowels (e, i) are preserved — they are more perceptually salient and historically stable in Celtic unstressed syllables. Stressed syllable protected by skip_stress.",
        "old_list": ["a", "o", "u"],
        "new_list": ["ɨ", "ɨ", "ɨ"],
        "pre_trig": [], "post_trig": [], "pre_ex": [], "post_ex": [],
        "skip_stress": True, "stress_solo": False,
    }),
    (115, {
        "name": "Unstressed long vowel shortening",
        "type": "con",
        "notes": "Long vowels in unstressed syllables shorten but survive as full short vowels (not reduced to ɨ). Two-tier reduction: short → ɨ (deleted), long → short (survives). Stressed long vowels protected.",
        "old_list": ["aː", "eː", "iː", "oː", "uː"],
        "new_list": ["a", "e", "i", "o", "u"],
        "pre_trig": [], "post_trig": [], "pre_ex": [], "post_ex": [],
        "skip_stress": True, "stress_solo": False,
    }),
    (120, {
        "name": "ɨ deletion",
        "type": "del",
        "notes": "Deletes /ɨ/ unconditionally. sonority_safe=True prevents deletion where it would create an unlicensable onset cluster. Handles both open-syllable syncope and word-final cleanup.",
        "del_list": ["ɨ"],
        "pre_list": [], "post_list": [],
        "except_pre": [], "except_post": [],
        "skip_stress": False, "stress_solo": False,
        "sonority_safe": True,
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
    print(f"\nDone. {len(RULES)} rules inserted into preset '{PRESET}'.")

if __name__ == "__main__":
    main()
