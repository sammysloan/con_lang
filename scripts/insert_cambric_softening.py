"""
Cambric softening rules.

Changes:
  Rule 70 patch – intervocalic p now → ɸ (bilabial) instead of f (labiodental).
    Keeps the labial place of articulation, softer than labiodental f.
    t→θ and k→x are unchanged.

  Rule 75 (new) – word-initial l → ɬ (voiceless lateral fricative).
    Welsh-style 'll'; gives Cambric its most distinctively Brythonic phoneme.

Run from project root: python3 scripts/insert_cambric_softening.py
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

V = ["au", "ai", "ei", "oi", "ou", "a", "e", "i", "o", "u",
     "aː", "eː", "iː", "oː", "uː"]

# Patched Rule 70: p → ɸ (bilabial fricative) instead of p → f (labiodental)
RULE_70_PATCHED = {
    "name": "Intervocalic lenition: voiceless stops",
    "type": "con",
    "notes": "Spirantisation of intervocalic voiceless stops: p→ɸ, t→θ, k→x. Bilabial ɸ preserves the labial place of p while softening it; contrasts with f (< proto-Celtic ɸ, Rule 50).",
    "old_list": ["p", "t", "k"],
    "new_list": ["ɸ", "θ", "x"],
    "pre_trig": V, "post_trig": V,
    "pre_ex": [], "post_ex": [],
    "skip_stress": False, "stress_solo": False,
}

# New Rule 75: word-initial l → ɬ
RULE_75 = {
    "name": "Word-initial l → ɬ",
    "type": "syll",
    "notes": "Word-initial /l/ devoices to the voiceless lateral fricative /ɬ/, cf. Welsh 'll' in llan, llwyd, llyn. Gives Cambric a distinctively Brythonic phoneme absent from Goidelic.",
    "old_list": ["l"],
    "new_list": ["ɬ"],
    "position": "first",
    "pre_list": ["*Blank"], "post_list": [],
    "skip_stress": False, "stress_solo": False,
}

def main():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Patch Rule 70
    cur.execute(
        "DELETE FROM presets WHERE preset_name=? AND rule_order=?",
        (PRESET, 70),
    )
    if cur.rowcount:
        print("Removed old Rule 70.")
    cur.execute(
        "INSERT INTO presets (preset_name, rule_order, rule) VALUES (?, ?, ?)",
        (PRESET, 70, json.dumps(RULE_70_PATCHED, ensure_ascii=False)),
    )
    print("  Inserted patched Rule 70: Intervocalic lenition (p→ɸ, t→θ, k→x)")

    # Add Rule 75
    cur.execute(
        "DELETE FROM presets WHERE preset_name=? AND rule_order=?",
        (PRESET, 75),
    )
    if cur.rowcount:
        print("Removed old Rule 75.")
    cur.execute(
        "INSERT INTO presets (preset_name, rule_order, rule) VALUES (?, ?, ?)",
        (PRESET, 75, json.dumps(RULE_75, ensure_ascii=False)),
    )
    print("  Inserted Rule 75: Word-initial l → ɬ")

    conn.commit()
    conn.close()
    print("\nDone. Softening rules applied to Cambric preset.")

if __name__ == "__main__":
    main()
