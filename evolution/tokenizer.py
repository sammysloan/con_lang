from typing import Iterable, List, Optional, Set
from evolution.ipa_dictionaries import IPA_GROUPS   # adjust if path differs
from itertools import product

class Tokenizer:
    # ... your existing Tokenizer code (unchanged) ...

    @staticmethod
    def detokenize(tokens: Iterable[str]) -> str:
        return "".join(tokens)


# === DEFAULT IPA UNITS BUILDER ===

def build_default_ipa_units() -> List[str]:
    """
    Build a robust default unit set using IPA_GROUPS plus some common extras.
    Sorted by length desc to enable greedy longest-match tokenization.
    """
    units: Set[str] = set()

    # Add all short vowels and their lengthened/nasalized forms
    for v in IPA_GROUPS.get("ShortVowels", []):
        units.add(v)
        units.add(v + "ː")
        units.add(v + "ːː")
        units.add(v + "̃")
        units.add(v + "̃ː")
        units.add(v + "̃ːː")

    # Add diphthongs if defined, else generate from ShortVowels
    dips = IPA_GROUPS.get("Diphthongs", [])
    if not dips:
        dips = [a + b for a in IPA_GROUPS.get("ShortVowels", []) for b in IPA_GROUPS.get("ShortVowels", []) if a != b]
    units.update(dips)

    # Add consonants, affricates, and extras
    for key in ["Consonants", "Nasals", "Plosives", "SibilantAffricates", "NonSibilantAffricates",
                "SibilantFricatives", "NonSibilantFricatives", "Approximants", "Taps", "Trills",
                "LateralAffricates", "LateralFricatives", "LateralApproximants", "LateralTaps",
                "Glottal", "Uvular", "Velar", "Palatal", "Retroflex", "PostAlveolar", "Alveolar", "Dental",
                "Labiodental", "Bilabial"]:
        units.update(IPA_GROUPS.get(key, []))

    # Always include stress/length markers as standalone
    units.update({"ˈ", "ˌ", "ː", "̃", "."})

    return sorted(units, key=len, reverse=True)


# Expose default units at module level
DEFAULT_IPA_UNITS: List[str] = build_default_ipa_units()

__all__ = ["Tokenizer", "build_default_ipa_units", "DEFAULT_IPA_UNITS"]

class Tokenizer:
    """
    Greedy longest-match tokenizer with optional legality constraints.

    Modes:
      - strict_compounds=True: multi-char matches are only accepted if present
        in `legal_compounds` (if provided). Otherwise they are split.
      - strict_compounds=False: any multi-char unit present in `units` can match.

    You can flip modes at runtime (e.g., strict for `to_ipa`, permissive for evolution).
    """
    def __init__(
        self,
        units: Iterable[str],
        legal_units: Optional[Iterable[str]] = None,
        legal_compounds: Optional[Iterable[str]] = None,
        strict_compounds: bool = False
    ):
        # master inventory the tokenizer is allowed to recognize
        self._unit_set: Set[str] = set(u for u in units if u)
        self.units: List[str] = sorted(self._unit_set, key=len, reverse=True)

        # optional limiters
        self.legal_units: Optional[Set[str]] = set(legal_units) if legal_units else None
        self.legal_compounds: Optional[Set[str]] = set(legal_compounds) if legal_compounds else None

        # mode
        self.strict_compounds = strict_compounds

    # ---- public toggles -------------------------------------------------

    def set_strict(self, on: bool = True) -> None:
        self.strict_compounds = on

    def set_permissive(self) -> None:
        self.strict_compounds = False

    def set_legal_units(self, seq: Optional[Iterable[str]]) -> None:
        self.legal_units = set(seq) if seq else None

    def set_legal_compounds(self, seq: Optional[Iterable[str]]) -> None:
        self.legal_compounds = set(seq) if seq else None

    def add_units(self, new_units: Iterable[str]) -> None:
        changed = False
        for u in new_units:
            if u and u not in self._unit_set:
                self._unit_set.add(u)
                changed = True
        if changed:
            self.units = sorted(self._unit_set, key=len, reverse=True)

    # ---- core tokenization ----------------------------------------------


    def _is_allowed(self, cand: str) -> bool:
        """Check legality gates for a candidate unit."""
        # If a full legal_units list is supplied, it constrains everything.
        if self.legal_units is not None and cand not in self.legal_units:
            return False

        # If strict mode and candidate is multi-char, it must be in legal_compounds.
        if self.strict_compounds and len(cand) > 1:
            if self.legal_compounds is None:
                return False  # no compounds are legal unless whitelisted
            return cand in self.legal_compounds

        return True

    def tokenize(self, text: str) -> List[str]:
        tokens: List[str] = []
        i = 0
        n = len(text)

        while i < n:
            matched = None

            # try longest-first
            for u in self.units:
                if not text.startswith(u, i):
                    continue
                if self._is_allowed(u):
                    matched = u
                    break

            # fallback: single char (even if not in units)
            if matched is None:
                matched = text[i]

            tokens.append(matched)
            i += len(matched)
        return tokens

    # small helpers
    @staticmethod
    def detokenize(tokens: Iterable[str]) -> str:
        return "".join(tokens)
