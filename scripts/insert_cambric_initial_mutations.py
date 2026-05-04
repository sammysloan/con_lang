"""
Insert Cambric evolution preset – Word-initial consonant mutations (rules 63–64).
Run from project root: python3 scripts/insert_cambric_initial_mutations.py

Rule 63: Word-initial s → h before vowels (Proto-Brythonic innovation)
Rule 64: Word-initial r → r̥ (devoicing; cf. Welsh 'rh')

Both are Proto-Brythonic changes contemporary with w→ɡw (60) and l→ɬ (75),
slotted between them in the rule order.
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

# Vowels that trigger s → h: only pre-vocalic word-initial s weakens.
# Consonant-initial clusters like *sp-, *st-, *sk- are unaffected.
_VOWELS = ["a", "e", "i", "o", "u", "aː", "eː", "iː", "oː", "uː"]

RULES = [
    (63, {
        "name": "Word-initial s → h",
        "type": "syll",
        "notes": "Proto-Brythonic: word-initial /s/ weakens to /h/ before a vowel. Restricted to pre-vocalic position — consonant clusters like *sp-, *st-, *sk- are unaffected. Cf. Welsh hen < *senos, haf < *samos, hir < *sīros. Goidelic retains /s/ in the same position.",
        "old_list": ["s"],
        "new_list": ["h"],
        "position": "first",
        "pre_list": ["*Blank"],
        "post_list": _VOWELS,
        "skip_stress": False,
        "stress_solo": False,
    }),
    (64, {
        "name": "Word-initial r → r̥",
        "type": "syll",
        "notes": "Proto-Brythonic devoicing of word-initial /r/ to the voiceless trill /r̥/, written 'rh' in Welsh. Sister change to l → ɬ (Rule 75) — both are initial-consonant devoicings from the same period. Cf. Welsh rhan, rhy, rhoi. Goidelic retains voiced /r/.",
        "old_list": ["r"],
        "new_list": ["r̥"],
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
