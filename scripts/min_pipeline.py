# scripts/min_pipeline.py
# Usage:
#   python scripts/min_pipeline.py "An nescis, mi fili, quantilla prudentia mundus regatur?"
# or:
#   echo "An nescis, mi fili, quantilla prudentia mundus regatur?" | python scripts/min_pipeline.py

import os, sys, re

# Make project importable when run from anywhere
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.latin import PhonoLatin  # base-language pipeline

def latin_ipa_line(line: str) -> str:
    # 1) Normalize dashes to spaces, remove simple punctuation, lowercase
    norm = (
        line.replace("\u2011", " ")
            .replace("\u2013", " ")
            .replace("\u2014", " ")
            .replace("-", " ")
    )
    cleaned = re.sub(r"[.,;:!?()\[\]{}\"'…]", "", norm).strip().lower()
    if not cleaned:
        return ""

    # 2) Build Latin phonologizer with stress overrides
    overrides = os.path.join(ROOT, "data", "latin_stress_overrides.json")
    lat = PhonoLatin(override_path=overrides)

    # 3) Orthography -> IPA (with syllable dots and stress)
    words = cleaned.split()
    ipa_words = [lat.to_ipa(w) for w in words]
    return " ".join(ipa_words)

def main():
    if not sys.stdin.isatty():
        # Piped input
        text = sys.stdin.read()
    else:
        # Arg or prompt
        text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("> ")

    for line in text.splitlines():
        out = latin_ipa_line(line)
        if out:
            print(out)

if __name__ == "__main__":
    main()
