"""
Insert Cambric cluster-repair rules (125–128).

125 – Progressive devoicing: voiced stop after ANY voiceless consonant (profɡ → profk, kelstb → kelsp)
126 – Regressive devoicing: voiced fricative before voiceless consonant (fivt → fift)
127 – Svarabhakti epenthesis: insert /i/ before word-final sonorant after consonant or glide
      (elbn → elbin, moːθr → moːθir, diːwn → diːwin, cf. Irish máthair, bráthair)
128 – ɨ → i fallback: residual ɨ (blocked from deletion by sonority_safe) surfaces as short /i/
      (riː.ɨnt → riːint)

Run from project root: python3 scripts/insert_cambric_cluster_rules.py
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

VOICELESS_FRICATIVES = ["f", "θ", "x", "s"]
VOICELESS_STOPS      = ["p", "t", "k"]
VOICELESS_OBSTRUENTS = VOICELESS_FRICATIVES + VOICELESS_STOPS

RULES = [
    (125, {
        "name": "Cluster devoicing: voiced stop after voiceless consonant",
        "type": "con",
        "notes": "Progressive devoicing: voiced stops devoice when preceded by any voiceless consonant (stop or fricative). Repairs obstruent clusters created by ɨ deletion: profɡ→profk, kelstb→kelstp.",
        "old_list": ["b", "d", "ɡ"],
        "new_list": ["p", "t", "k"],
        "pre_trig": VOICELESS_OBSTRUENTS,
        "post_trig": [], "pre_ex": [], "post_ex": [],
        "skip_stress": False, "stress_solo": False,
    }),
    (126, {
        "name": "Cluster devoicing: voiced fricative before voiceless consonant",
        "type": "con",
        "notes": "Regressive devoicing: voiced fricatives devoice before voiceless consonants. Repairs clusters after ɨ deletion: fivt→fift, elðs→elθs.",
        "old_list": ["v", "ð"],
        "new_list": ["f", "θ"],
        "pre_trig": [],
        "post_trig": VOICELESS_OBSTRUENTS,
        "pre_ex": [], "post_ex": [],
        "skip_stress": False, "stress_solo": False,
    }),
    (127, {
        "name": "Svarabhakti epenthesis",
        "type": "epen",
        "notes": "Old Irish-style epenthetic /i/ before word-final sonorant (n, m, r, l) when preceded by a consonant or glide. Breaks up final clusters: biθn→biθin, moːθr→moːθir (cf. Irish máthair), diːwn→diːwin.",
        "find_list": ["n", "m", "r", "l"],
        "replace_list": ["in", "im", "ir", "il"],
        "syllable_pos": "last",
        "pre_list": ["*Consonants", "w", "j"],
        "post_list": [""],
    }),
    (128, {
        "name": "ɨ → i fallback",
        "type": "con",
        "notes": "Residual /ɨ/ that could not be deleted (sonority_safe blocked deletion) surfaces as short /i/. Prevents abstract ɨ from appearing in the surface form: riːɨnt→riːint.",
        "old_list": ["ɨ"],
        "new_list": ["i"],
        "pre_trig": [], "post_trig": [], "pre_ex": [], "post_ex": [],
        "skip_stress": False, "stress_solo": False,
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
