"""
Test the Cambric evolution preset against Proto-Celtic words.
Run from project root: python scripts/test_cambric.py
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.celtic import PhonoCeltic
from evolution.evolver import EvolutionEngine

DB_PATH = os.path.join(ROOT, "presets", "presets.db")
PRESET  = "Cambric"

# Proto-Celtic test words (Wiktionary reconstructions, *-prefix stripped by PhonoCeltic)
# Format: (proto-celtic-form, gloss)
TEST_WORDS = [
    # Basic vocabulary
    ("sindos",     "this/the"),
    ("māros",      "great"),
    ("bitus",      "world/life"),
    ("rūskos",     "bark (tree)"),
    ("kattā",      "cat"),
    ("nertos",     "strength"),
    ("dubnos",     "deep/world"),
    ("auros",      "gold"),
    ("senā",       "old (f.)"),
    ("wiros",      "man/true"),
    ("nouīos",     "new"),
    ("toutā",      "tribe/people"),
    # Long vowels (to test shift rule)
    ("māter",      "mother"),
    ("brātīr",     "brother"),
    ("rīgos",      "king (gen.)"),
    ("dūnom",      "fort (acc.)"),
    ("dūnos",      "fort (nom.)"),
    # Geminates (to test degemination)
    ("kattā",      "cat"),
    ("allā",       "other (f.)"),
    ("penno",      "head"),
    # Final -n (accusative)
    ("wīron",      "man (acc.)"),
    ("bitun",      "world (acc.)"),
    # Monosyllables (stress = only syllable, apocope should NOT fire)
    ("tīr",        "land"),
    ("nox",        "night"),

    # ── Batch 3 targets ──────────────────────────────────────────────────────
    # Diphthong monophthongization  (Rule 100)
    ("auros",      "gold"),          # au → oː  (cf. Irish ór)
    ("deiwos",     "god"),           # ei → iː  (cf. Welsh duw)
    ("noibos",     "holy"),          # oi → oː
    # I-affection  (Rule 105: stressed vowel fronts before following /i/)
    ("albinoː",    "white/bright"),  # a in stressed 'al' fronts → e before following i
    ("maginos",    "youth/son"),     # a in stressed 'mag' fronts → e before following i
    # Unstressed reduction  (Rules 110–115)
    ("brātīr",     "brother"),       # unstressed iː shortens → i
    ("profugos",   "fugitive"),      # unstressed u → ɨ → deleted (open syll)
    ("rīganos",    "queen"),         # unstressed a,o → ɨ; tests full chain
    # ── Batch 2 targets ──────────────────────────────────────────────────────
    # ɸ → f  (Rule 5)
    ("uɸelos",     "high"),          # ɸ survives to Batch 2, then → f

    # word-initial w → ɡw  (Rule 6)
    ("wiros",      "man/true"),      # w → ɡw
    ("wīron",      "man (acc.)"),    # w → ɡw

    # intervocalic voiceless stop lenition  (Rule 7: p→f, t→θ, k→x)
    ("māter",      "mother"),        # medial t between oː and e → θ
    ("brātīr",     "brother"),       # medial t between oː and iː → θ
    ("bitunom",    "forest"),        # medial t between i and u → θ  (after batch-1 apocope keeps it medial)

    # intervocalic voiced stop lenition  (Rule 8: b→v, d→ð, g→ɣ)
    ("fibeti",     "he drinks"),     # ɸ→f AND medial b between vowels → v
    ("rīganos",    "queen"),         # medial g between iː and a → ɣ → ∅ (Rules 8+9)
    ("epos",       "horse"),         # medial p → f  (intervocalic)

    # ── Spirantization targets (Rules 130–132) ───────────────────────────────
    # *makkʷos: geminate labiovelar → both kʷ→p (P-Celtic) → degeminate → map
    #           → word-final p→f (Rule 130) → f→θ (Rule 131) → a→æ (Rule 132)
    ("makʷkʷos",  "son/patronymic"), # → mæθ  (Cambric patronymic particle)
    # Word-final t→θ after vowel (Rule 130)
    ("kattā",      "cat"),           # kat → kaθ → kæθ
    ("bitus",      "world/life"),    # bit → biθ
    ("toutā",      "tribe/people"),  # tuːt → tuːθ
    # Word-final t→θ after sonorant (Rule 130; cf. Welsh nerth)
    ("nertos",     "strength"),      # nert → nerθ
    # Word-final p→f→θ chain (Rules 130+131)
    ("epos",       "horse"),         # ep → ef → eθ
]

def load_rules():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute(
        "SELECT rule FROM presets WHERE preset_name=? ORDER BY rule_order",
        (PRESET,)
    )
    rules = [json.loads(row[0]) for row in cur.fetchall()]
    conn.close()
    return rules

def run(words, rules, verbose=False):
    pc = PhonoCeltic()
    print(f"{'Proto-Celtic':<16} {'IPA (input)':<22} {'→  Evolved':<22} {'Gloss'}")
    print("-" * 72)
    for form, gloss in words:
        ipa_in = pc.to_ipa(form)
        engine = EvolutionEngine([ipa_in], log_steps=verbose)
        engine.evolve(rules)
        result = engine.words[0].to_string()
        # strip stress marks for readability (keep them in verbose)
        display = result if verbose else result.replace("ˈ","").replace(".","")
        print(f"*{form:<15} {ipa_in:<22} →  {display:<20} {gloss}")
        if verbose:
            engine.words[0].print_history()

def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    rules = load_rules()
    if not rules:
        print(f"No rules found for preset '{PRESET}'. Run insert_cambric_batch1.py first.")
        sys.exit(1)
    print(f"Loaded {len(rules)} rule(s) from preset '{PRESET}'.\n")
    run(TEST_WORDS, rules, verbose=verbose)

if __name__ == "__main__":
    main()
