"""
Insert Cambric evolution preset – Word-final spirantization (rules 130–132).
Run from project root: python3 scripts/insert_cambric_spirantization.py

Three-stage chain:
  Rule 130: Word-final stop spirantization — p→f, t→θ, k→x (after vowel/sonorant)
  Rule 131: Word-final f→θ (closes the p→f→θ chain; labial merges with dental)
  Rule 132: Pre-fricative a-fronting — a→æ before word-final {f, θ, x}
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

# Voiceless stops only spirantize after a vowel or sonorant —
# preserves clusters like -sk, -fk (stops after obstruents are left alone).
_PRE_VOWELS_AND_SONORANTS = [
    "a", "e", "i", "o", "u", "æ",
    "aː", "eː", "iː", "oː", "uː",
    "r", "l", "n", "m", "ɬ", "ɾ", "w", "j",
]

RULES = [
    (130, {
        "name": "Word-final stop spirantization",
        "type": "syll",
        "notes": "Celtic aspirate-mutation pattern in coda position: word-final voiceless stops spirantize after a vowel or sonorant — p→f, t→θ, k→x. Restricted to vowel/sonorant context to preserve clusters like -sk and -fk. Cf. Welsh nerth < *nertos (t→θ), Welsh aspirate mutation p→ff.",
        "old_list": ["p", "t", "k"],
        "new_list": ["f", "θ", "x"],
        "position": "last",
        "pre_list": _PRE_VOWELS_AND_SONORANTS,
        "post_list": ["*Blank"],
        "skip_stress": False,
        "stress_solo": False,
    }),
    (131, {
        "name": "Word-final f → θ",
        "type": "syll",
        "notes": "Word-final /f/ (from spirantised /p/, Rule 130) neutralises to /θ/. Labial and dental word-final fricatives merge at the dental. Distinctive Cambric innovation; gives the patronymic its -θ ending: *makkʷos → mæθ.",
        "old_list": ["f"],
        "new_list": ["θ"],
        "position": "last",
        "pre_list": [],
        "post_list": ["*Blank"],
        "skip_stress": False,
        "stress_solo": False,
    }),
    (132, {
        "name": "Pre-fricative a-fronting",
        "type": "syll",
        "notes": "Short /a/ fronts to /æ/ before a word-final fricative {f, θ, x}. Anticipatory assimilation: the open vowel advances toward the constricted articulation of the following fricative. Cf. Cambric mæθ < *makkʷos, kæθ < *kattā.",
        "old_list": ["a"],
        "new_list": ["æ"],
        "position": "last",
        "pre_list": [],
        "post_list": ["f", "θ", "x"],
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
