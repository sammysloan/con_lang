"""
Insert the 'Proto West Germanic' preset into presets.db.

Run from the project root:
    python scripts/insert_proto_west_germanic.py

Rule order matches the chronological / feeding order described in the session notes.
"""
import json
import os
import shutil
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "presets", "presets.db")

PRESET_NAME = "Proto West Germanic"

RULES = [
    # ── 1. Rhotacism ────────────────────────────────────────────────────────
    # *z → r everywhere.  Must run FIRST: later rules operate on the /r/ it
    # creates (final-r loss) and on the absence of /z/ (gemination list).
    {
        "name": "Rhotacism",
        "type": "con",
        "notes": "PGmc - *z rotacizes to /r/ in all environments. Feeds final-r loss.",
        "old_list":  ["z"],
        "new_list":  ["r"],
        "pre_trig":  [], "post_trig": [],
        "pre_ex":    [], "post_ex":   [],
        "skip_stress": False, "stress_solo": False,
    },

    # ── 2. Loss of word-final -r (< *-z) ────────────────────────────────────
    # The nominative -z → -r (rule 1) → ∅ word-finally.
    # Must follow rhotacism so we target /r/, not the original /z/.
    {
        "name": "Loss of final -r",
        "type": "del",
        "notes": "W. Gmc - Word-final /r/ (< *-z) is lost. Requires rhotacism first.",
        "del_list":   ["r"],
        "pre_list":   [],
        "post_list":  ["*Blank"],
        "except_pre": [], "except_post": [],
        "skip_stress": False, "stress_solo": False, "sonority_safe": True,
    },

    # ── 3. West Germanic consonant gemination ───────────────────────────────
    # C → CC before /j/ (except /r/, which does not geminate).
    # Must run BEFORE j-loss: the gemination IS triggered by /j/, so if /j/
    # were deleted first there would be nothing to trigger it.
    {
        "name": "West Germanic Gemination",
        "type": "con",
        "notes": "W. Gmc - Consonants (except /r/) geminate before /j/. Feeds j-loss.",
        "old_list": [
            "pj",  "bj",  "tj",  "dj",  "kj",  "ɡj",
            "ɸj",  "θj",  "xj",  "sj",
            "mj",  "nj",  "ŋj",
            "lj",
            "βj",  "ðj",  "ɣj",
        ],
        "new_list": [
            "ppj", "bbj", "ttj", "ddj", "kkj", "ɡɡj",
            "ɸɸj", "θθj", "xxj", "ssj",
            "mmj", "nnj", "ŋŋj",
            "llj",
            "ββj", "ððj", "ɣɣj",
        ],
        "pre_trig":  [], "post_trig": [],
        "pre_ex":    [], "post_ex":   [],
        "skip_stress": False, "stress_solo": False,
    },

    # ── 4. Loss of post-consonantal /j/ ─────────────────────────────────────
    # After gemination the triggering /j/ is deleted.
    # Must follow gemination (rule 3): order matters because rule 3 *reads*
    # the /j/ to decide whether to geminate.
    {
        "name": "Loss of post-consonantal j",
        "type": "del",
        "notes": "W. Gmc - /j/ is lost after consonants (post-gemination cleanup). Requires gemination first.",
        "del_list":   ["j"],
        "pre_list":   ["*Consonants"],
        "post_list":  [],
        "except_pre": [], "except_post": [],
        "skip_stress": False, "stress_solo": False, "sonority_safe": True,
    },

    # ── 5a. Ingvaeonic nasal spirant law – compensatory lengthening ──────────
    # VN + fricative → V̄N + fricative  (lengthen the vowel first).
    # Must run BEFORE deletion (rule 5b): if the nasal is gone, the
    # conditioning environment for lengthening no longer exists.
    {
        "name": "Nasal Spirant Law - Lengthening",
        "type": "con",
        "notes": "Ingvaeonic - Vowel lengthens before nasal + fricative. Must precede nasal deletion (part 1 of 2).",
        "old_list": [
            "ɑn", "ɑm",
            "ɛn", "ɛm",
            "in", "im",
            "ɔn", "ɔm",
            "un", "um",
        ],
        "new_list": [
            "ɑːn", "ɑːm",
            "ɛːn", "ɛːm",
            "iːn", "iːm",
            "ɔːn", "ɔːm",
            "uːn", "uːm",
        ],
        "pre_trig":  [],
        "post_trig": ["*Fricatives"],
        "pre_ex":    [], "post_ex": [],
        "skip_stress": False, "stress_solo": False,
    },

    # ── 5b. Ingvaeonic nasal spirant law – nasal deletion ───────────────────
    # V̄N + fricative → V̄ + fricative  (delete the nasal).
    # Must follow lengthening (rule 5a): by this point the vowel is already
    # long, so deleting the nasal is safe and leaves the lengthened nucleus.
    {
        "name": "Nasal Spirant Law - Deletion",
        "type": "del",
        "notes": "Ingvaeonic - Nasal deleted before fricative. Requires compensatory lengthening first (part 2 of 2).",
        "del_list":   ["n", "m"],
        "pre_list":   [],
        "post_list":  ["*Fricatives"],
        "except_pre": [], "except_post": [],
        "skip_stress": False, "stress_solo": False, "sonority_safe": True,
    },
]


def insert_preset(preset_name: str, rules: list[dict]) -> None:
    if not os.path.exists(DB_PATH):
        print(f"[Error] Database not found: {DB_PATH}")
        return

    # Backup first
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_PATH + f".backup_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup created: {backup_path}")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Warn if preset already exists
        cursor.execute("SELECT COUNT(*) FROM presets WHERE preset_name = ?", (preset_name,))
        (count,) = cursor.fetchone()
        if count:
            print(f"[Warning] Preset '{preset_name}' already exists — overwriting.")
            cursor.execute("DELETE FROM presets WHERE preset_name = ?", (preset_name,))

        for order, rule in enumerate(rules):
            cursor.execute(
                "INSERT INTO presets (preset_name, rule_order, rule) VALUES (?, ?, ?)",
                (preset_name, order, json.dumps(rule, ensure_ascii=False)),
            )

        conn.commit()

    print(f"Inserted {len(rules)} rules into preset '{preset_name}'.")


if __name__ == "__main__":
    insert_preset(PRESET_NAME, RULES)
