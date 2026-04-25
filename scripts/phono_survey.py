"""
scripts/phono_survey.py
Run: python scripts/phono_survey.py

Produces a phonological survey of the Marcher preset by running a curated
set of Latin words through the full Latin→IPA→Marcher pipeline. Words are
grouped by the phonological feature they are meant to illustrate.
"""

import sys, os, json, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.latin import PhonoLatin
from evolution.evolver import EvolutionEngine

DB_PATH    = os.path.join(ROOT, "presets", "presets.db")
OVER_PATH  = os.path.join(ROOT, "data", "latin_stress_overrides.json")

# ── helpers ──────────────────────────────────────────────────────────────────

def load_marcher_rules():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT rule FROM presets WHERE preset_name='Marcher' ORDER BY rule_order"
        )
        return [json.loads(r[0]) for r in cur.fetchall()]

def run(lat, rules, words):
    """words: list of (label, latin_str) or latin_str. Returns list of result rows."""
    rows = []
    for item in words:
        if isinstance(item, tuple):
            label, latin = item
        else:
            label, latin = item, item
        try:
            ipa_in = lat.to_ipa(latin.lower())
            engine = EvolutionEngine([ipa_in])
            engine.evolve(rules)
            ipa_out = engine.words[0].to_string()
        except Exception as e:
            ipa_in, ipa_out = "ERROR", str(e)
        rows.append((label, ipa_in, ipa_out))
    return rows

def show(section, rows):
    print(f"\n{'─'*60}")
    print(f"  {section}")
    print(f"{'─'*60}")
    print(f"  {'LATIN':<16} {'IPA IN':<22} {'MARCHER IPA'}")
    print(f"  {'─'*14} {'─'*20} {'─'*20}")
    for label, ipa_in, ipa_out in rows:
        print(f"  {label:<16} {ipa_in:<22} {ipa_out}")

# ── survey corpus ─────────────────────────────────────────────────────────────

SECTIONS = [

    ("STRESSED VOWELS — /a e i o u/ and /au/", [
        ("pater",    "pater"),     # a
        ("tempus",   "tempus"),    # e
        ("piscis",   "piscis"),    # i
        ("portus",   "portus"),    # o
        ("luna",     "luna"),      # u
        ("aurum",    "aurum"),     # au diphthong (preserved)
        ("causa",    "causa"),     # au diphthong
        ("caelum",   "caelum"),    # ae → e (monophthongisation)
        ("poena",    "poena"),     # oe → e
    ]),

    ("I-AFFECTION (back vowel fronts before i/ɪ)", [
        ("ovilis",   "ovilis"),    # o → e before -i-
        ("turris",   "turris"),    # u → ɨ before -i-
        ("animus",   "animus"),    # a → ɛ before -i-
        ("bonus",    "bonus"),     # no i follows — o unchanged
        ("filius",   "filius"),    # i-stem, should front preceding vowel
        ("militia",  "militia"),
    ]),

    ("UNSTRESSED VOWEL REDUCTION → /ɨ/", [
        ("dominus",  "dominus"),   # unstressed o,u → ɨ
        ("femina",   "femina"),
        ("tabula",   "tabula"),
        ("populus",  "populus"),
    ]),

    ("WORD-INITIAL CONSONANTS — stops", [
        ("pater",    "pater"),     # p
        ("bellum",   "bellum"),    # b
        ("terra",    "terra"),     # t
        ("deus",     "deus"),      # d
        ("corpus",   "corpus"),    # k
        ("gladius",  "gladius"),   # g
    ]),

    ("WORD-INITIAL CONSONANTS — fricatives & sonorants", [
        ("faber",    "faber"),     # f
        ("vinum",    "vinum"),     # w → v
        ("salus",    "salus"),     # s (non-cluster)
        ("mater",    "mater"),     # m
        ("nomen",    "nomen"),     # n
        ("locus",    "locus"),     # l
    ]),

    ("WORD-INITIAL /r/ → /r̥/ (Brythonic devoicing)", [
        ("regula",   "regula"),
        ("rex",      "rex"),
        ("ripa",     "ripa"),
        ("rota",     "rota"),
    ]),

    ("INTERVOCALIC LENITION: p→b, t→d", [
        ("caput",    "caput"),     # intervocalic p → b
        ("vita",     "vita"),      # intervocalic t → d
        ("ripa",     "ripa"),      # intervocalic p
        ("pedes",    "pedes"),     # intervocalic d (already voiced)
    ]),

    ("INTERVOCALIC SPIRANTIZATION: b→v, d→ð, (g→ɣ→Ø or word-final g)", [
        ("liber",    "liber"),     # b → v
        ("cadere",   "cadere"),    # d → ð
        ("pedes",    "pedes"),     # d → ð
        ("video",    "video"),     # d → ð
        ("toga",     "toga"),      # g → ɣ → deleted (intervocalic)
        ("focus",    "focus"),     # k → ɣ → deleted (intervocalic)
        ("vicus",    "vicus"),     # k → ɣ → final g (after apocope)
    ]),

    ("YOD-COALESCENCE: ti→ʃ, di→ʒ, si→ʃ (before vowel)", [
        ("ratio",    "ratio"),     # ti+V → ʃ
        ("natio",    "natio"),
        ("pretium",  "pretium"),
        ("medium",   "medium"),    # di+V → ʒ
        ("radius",   "radius"),
        ("basium",   "basium"),    # si+V → ʃ
    ]),

    ("P-CELTIC SHIFT: kʷ→p, ɡʷ→b", [
        ("quinque",  "quinque"),   # kʷ → p
        ("aquila",   "aquila"),    # kʷ → p
        ("qualis",   "qualis"),
    ]),

    ("PROTHETIC /ɨ/ before word-initial s+C", [
        ("spiritus",  "spiritus"),
        ("stella",    "stella"),
        ("statio",    "statio"),
        ("schola",    "schola"),
        ("scala",     "scala"),
    ]),

    ("APOCOPE & LOSS OF FINAL -s", [
        ("luna",     "luna"),      # final -a deleted
        ("bonus",    "bonus"),     # -us: final s deleted, then -u deleted
        ("nomen",    "nomen"),     # -en stays? or final vowel?
        ("pater",    "pater"),     # -er: r survives
        ("rex",      "rex"),       # ks → s, then final s deleted
        ("mons",     "mons"),      # final n deleted, then s deleted
    ]),

    ("CONSONANT CLUSTERS (surviving onset clusters)", [
        ("frater",   "frater"),    # fr
        ("tres",     "tres"),      # tr
        ("primus",   "primus"),    # pr
        ("planta",   "planta"),    # pl
        ("bracchium","bracchium"), # br (+ degemination)
        ("clarus",   "clarus"),    # kl
        ("mundus",   "mundus"),    # nd
        ("campus",   "campus"),    # mp
    ]),

]

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    lat   = PhonoLatin(override_path=OVER_PATH)
    rules = load_marcher_rules()

    print("\n" + "═"*60)
    print("  MARCHER PHONOLOGICAL SURVEY")
    print("═"*60)

    collected_outputs = set()

    for section_name, corpus in SECTIONS:
        rows = run(lat, rules, corpus)
        show(section_name, rows)
        for _, _, ipa_out in rows:
            # strip stress and syllable markers to harvest bare segments
            stripped = ipa_out.replace("ˈ", "").replace(".", "")
            collected_outputs.add(stripped)

    # Derive a rough segment inventory from all outputs
    import re
    multi = re.compile(
        r'r̥|au|ɛ|ɪ|ɔ|ʊ|ɨ|ɑ|ʃ|ʒ|ɣ|ð|ŋ|[a-z]'
    )
    segments = set()
    for form in collected_outputs:
        segments.update(multi.findall(form))

    print("\n" + "═"*60)
    print("  ATTESTED SEGMENTS (derived from survey output)")
    print("═"*60)

    vowels = {s for s in segments if s in "aeiouɛɪɔʊɨɑ" or s == "au"}
    cons   = segments - vowels
    print(f"\n  Vowels:     {' '.join(sorted(vowels))}")
    print(f"  Consonants: {' '.join(sorted(cons))}\n")


if __name__ == "__main__":
    main()
