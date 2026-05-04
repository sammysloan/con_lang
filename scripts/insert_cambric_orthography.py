"""
Insert Cambric orthography preset into presets/orthographies.db.
Run from project root: python3 scripts/insert_cambric_orthography.py

Conventions:
  - Based on Marcher/Welsh: c=/k/, ll=/ɬ/, th=/θ/, dd=/ð/, ff=/f/, f=/v/, rh=/r̥/, gw=/ɡw/
  - Gaelic additions: ch=/x/ (gives "noch", "rhúsc"), acute fada for long vowels (ó, ú, í, é, á)
  - /æ/ written as plain <a>  — predictable before word-final fricatives, matches Welsh "cath"
  - /ə/ written as <e> — Welsh-style schwa; contextually unambiguous (always unstressed)
"""
import os, sys, sqlite3, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

ODB_PATH = os.path.join(ROOT, "presets", "orthographies.db")
NAME = "Cambric"

MAP = [
    # Multi-char sequences (longest match wins, but listed first for clarity)
    ["ɡj", "gy"],
    ["ɡw", "gw"],
    ["r̥",  "rh"],
    # Long vowels — ː preserved by orthographer so these fire correctly
    ["oː", "ó"],
    ["uː", "ú"],
    ["iː", "í"],
    ["eː", "é"],
    ["aː", "á"],
    # Digraphs
    ["ɬ",  "ll"],
    ["θ",  "th"],
    ["ð",  "dd"],
    ["x",  "ch"],
    ["ŋ",  "ng"],
    # Single consonants
    ["k",  "c"],
    ["ɡ",  "g"],
    ["f",  "ff"],
    ["v",  "f"],
    ["p",  "p"],
    ["b",  "b"],
    ["t",  "t"],
    ["d",  "d"],
    ["s",  "s"],
    ["h",  "h"],
    ["m",  "m"],
    ["n",  "n"],
    ["r",  "r"],
    ["l",  "l"],
    ["w",  "w"],
    ["j",  "y"],
    # Vowels
    ["ə",  "e"],
    ["æ",  "a"],
    ["a",  "a"],
    ["e",  "e"],
    ["i",  "i"],
    ["o",  "o"],
    ["u",  "u"],
]


def main():
    conn = sqlite3.connect(ODB_PATH)
    cur  = conn.cursor()

    # Ensure table exists (mirrors orthographies.db schema)
    cur.execute(
        "CREATE TABLE IF NOT EXISTS orth_presets (name TEXT PRIMARY KEY, data TEXT)"
    )

    data = json.dumps({"options": None, "map": MAP}, ensure_ascii=False)
    cur.execute(
        "INSERT OR REPLACE INTO orth_presets (name, data) VALUES (?, ?)",
        (NAME, data),
    )
    conn.commit()
    conn.close()
    print(f"Inserted orthography preset '{NAME}' ({len(MAP)} mappings).")


if __name__ == "__main__":
    main()
