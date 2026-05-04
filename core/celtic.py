# file: celtic.py
import json

try:
    # when running as a package (recommended)
    from core.phonologizer import Phonologizer
except ModuleNotFoundError:
    # when running directly from core/
    from phonologizer import Phonologizer

from evolution.tokenizer import Tokenizer, DEFAULT_IPA_UNITS
from evolution.ipa_dictionaries import IPA_GROUPS

# Wiktionary-style Proto-Celtic inventory
PC_DIPHTHONGS = {"ai", "au", "ei", "oi", "ou", "āi", "āu"}

class PhonoCeltic(Phonologizer):
    def __init__(self, normalize_f_to_phi: bool = True, debug: bool = False, override_path=None):
        super().__init__(language="Celtic")
        self.debug = debug
        self.normalize_f_to_phi = normalize_f_to_phi

        # --- orthographic → IPA map (largely identity; long vowels get ː) ---
        self.ipa_map = {
            # Short vowels (orthography → IPA)
            'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u',
            # Long vowels with macrons
            'ā': 'aː', 'ē': 'eː', 'ī': 'iː', 'ō': 'oː', 'ū': 'uː',
            # Diphthongs (kept as sequences)
            'ai': 'ai', 'au': 'au', 'ei': 'ei', 'oi': 'oi', 'ou': 'ou',
            'āi': 'aːi', 'āu': 'aːu',
            # Consonants (IPA-ish identity)
            'p': 'p', 'b': 'b', 't': 't', 'd': 'd', 'k': 'k', 'g': 'ɡ',
            'm': 'm', 'n': 'n', 'r': 'r', 'l': 'l', 's': 's',
            'w': 'w', 'y': 'j',        # palatal glide outputs as [j]
            'ɸ': 'ɸ', 'β': 'β', 'x': 'x', 'z': 'z',
            # Labiovelars
            'kʷ': 'kʷ', 'gʷ': 'ɡʷ',
            # Convenience inputs (normalized in split step, but mapped here too)
            'c': 'k',
            # Bug/edge safety
            'ŋ': 'ŋ'
        }

        # --- vowel sets used by syllabifier (operate on IPA after mapping) ---
        self.vowels_core = {'a', 'e', 'i', 'o', 'u', 'aː', 'eː', 'iː', 'oː', 'uː'}
        self.diphthongs = set(PC_DIPHTHONGS)  # (orthographic grouping)
        # After mapping, diphthongs are sequences (e.g., 'ai'), keep them in vowel set:
        self.vowels = self.vowels_core | {'ai', 'au', 'ei', 'oi', 'ou', 'aːi', 'aːu'}

        # === Tokenizer wiring (match latin.py pattern) ===
        self.legal_units = None
        self.legal_compounds = set(PC_DIPHTHONGS) | {"kʷ", "ɡʷ"}

        self.tokenizer = Tokenizer(
            units=DEFAULT_IPA_UNITS,
            legal_units=self.legal_units,
            legal_compounds=self.legal_compounds,
            strict_compounds=True,
        )

    # ------------------------------------------------------------------ parent hooks

    def assign_stress(self, syllables):
        """
        Proto-Celtic stress is debated; by default we **do not** mark stress here.
        If you want a placeholder (e.g., initial stress), uncomment below.
        """
        # Example (optional) initial-stress behavior:
        # if syllables:
        #     syllables[0] = "ˈ" + syllables[0]
        return syllables

    def to_ipa(self, word: str, use_override: bool = True, verbose: bool = False) -> str:
        """
        Convert a Proto-Celtic (Wiktionary-style) input form to IPA:
        1) split into orthographic units (with normalization)
        2) apply orthographic context tweaks
        3) map units → IPA
        4) post-mapping cleanups
        5) syllabify for downstream rules
        6) (no stress by default) return dotted syllables (no stress mark)
        """
        original = word
        # 1) units from orthography (normalize here)
        units = self.split_into_phonological_units(word)

        # 2) orthographic/context rules (very light-touch)
        units = self.apply_context_rules(units)

        # 3) map to IPA
        mapped = [self.ipa_map.get(u, u) for u in units]

        # 4) post-mapping tweaks (operate on IPA)
        mapped = self.apply_post_mapping_rules(mapped)
        ipa_string = "".join(mapped)

        # 5) syllabify the IPA string (tokenizer splits IPA units)
        syllables = self.syllabify(self.tokenizer.tokenize(ipa_string))

        # 6) stress (no-op)
        stressed = self.assign_stress(syllables)

        final = ".".join(stressed)

        if verbose or self.debug:
            print(f"[PC] {original} → units:{units} → mapped:{mapped} → {final}")
        return final

    # ------------------------------------------------------ orthographic splitting

    def split_into_phonological_units(self, word):
        """
        Split Proto-Celtic input into units with normalization aligned to latin.py style.
        Normalizations:
          - Leading '*' is stripped.
          - Lowercase.
          - qu → kʷ, gu → gʷ
          - j → y  (input convenience; we output IPA [j] later)
          - optional f → ɸ (toggle by self.normalize_f_to_phi)
          - tolerate 'c' → maps to [k] via ipa_map
          - keep macrons ā ī ū
          - group diphthongs and labiovelars as single units
        """
        w = word.strip().lstrip("*").lower()

        # Simple digraph/trigraph grouping
        # Order matters: check longer sequences first.
        multis = ['kʷ', 'gʷ', 'qu', 'gu']  # qu/gu normalize to kʷ/gʷ below
        diph = ['āi', 'āu', 'ai', 'au', 'ei', 'oi', 'ou']

        i, n = 0, len(w)
        units = []
        while i < n:
            # try multi-char first
            if i + 1 < n:
                two = w[i:i+2]
                three = w[i:i+3] if i + 2 < n else ''
                # already-IPA labiovelars
                if three in ('kʷ', 'gʷ'):
                    units.append(three)
                    i += 3
                    continue
                if two in ('qu', 'gu'):
                    units.append(two)  # normalize later in apply_context_rules
                    i += 2
                    continue
                if two in diph:
                    units.append(two)
                    i += 2
                    continue
            # single char
            units.append(w[i])
            i += 1

        return units

    # ----------------------------------------------------- orthographic context rules

    def apply_context_rules(self, units):
        """
        Light orthographic/phonotactic tidy-ups BEFORE mapping to IPA.
        """
        out = []
        for u in units:
            # normalize j→y (users often type 'j' for the glide)
            if u == 'j':
                out.append('y')
                continue
            # normalize qu / gu to kʷ / gʷ (keep behavior consistent project-wide)
            if u == 'qu':
                out.append('kʷ')
                continue
            if u == 'gu':
                out.append('gʷ')
                continue
            # optional: f → ɸ (PC recon uses ɸ; many users type f)
            if self.normalize_f_to_phi and u == 'f':
                out.append('ɸ')
                continue
            out.append(u)
        return out

    # ----------------------------------------------------- post-mapping IPA rules

    def apply_post_mapping_rules(self, ipa_units):
        """
        Post-mapping is intentionally minimal (PC base stage).
        Examples kept meek to match latin.py’s pattern of a dedicated hook:
          - s → z between vowels (optional allophony).
          - k → x before s (so ks → xs).
        Remove these if you want strictly phonemic outputs.
        """
        def is_vowel(sym: str) -> bool:
            return (sym in self.vowels) or (sym in self.vowels_core)

        new = ipa_units[:]


        return new

    # ---------------------------------------------------------------- syllabifier

    def syllabify(self, units):
        """
        Conservative syllabifier (keeps close to latin.py structure):
        - Greedy onset where licit (basic liquid clusters + labiovelars)
        - Diphthongs count as nuclei
        - Outputs list of syllable strings (without stress marks)
        """
        vowels = self.vowels  # includes diphthongs and long nuclei
        # onsets allowed (tune as needed)
        onsets = {
            'pr','br','tr','dr','kr','ɡr','fr','mr',
            'pl','bl','kl','ɡl','fl','ml',
            'kʷ','ɡʷ','kw','sw',
            'sp', 'st', 'sk', 'sm', 'sn', 'sl'
        }

        syllables = []
        i, n = 0, len(units)
        while i < n:
            onset = []
            nucleus = []
            coda = []

            # 1) onset (max one consonant, or a listed cluster)
            if i < n and units[i] not in vowels:
                # try 2-unit onset clusters
                if i + 1 < n and (units[i] + units[i+1]) in onsets:
                    onset = [units[i] + units[i+1]]
                    i += 2
                else:
                    onset = [units[i]]
                    i += 1

            # 2) nucleus (must exist)
            if i < n:
                # diphthong as single nucleus
                if i + 1 < n and (units[i] + units[i+1]) in {'ai','au','ei','oi','ou','aːi','aːu'}:
                    nucleus = [units[i] + units[i+1]]
                    i += 2
                else:
                    nucleus = [units[i]]
                    i += 1
            else:
                # stray consonant at end
                if syllables:
                    syllables[-1] += "".join(onset)
                break

            # 3) greedy coda: pull following consonants until a vowel starts,
            # then leave last consonant(s) for next onset if a legal onset exists.
            j = i
            while j < n and units[j] not in vowels:
                coda.append(units[j])
                j += 1

            # Split coda to maximize next onset if possible
            if coda:
                # if last two can start an onset together, keep them for next syllable
                if len(coda) >= 2 and (coda[-2] + coda[-1]) in onsets:
                    keep_for_next = coda[-2:]
                    coda = coda[:-2]
                    i = j - 2
                # else if last one can onset, keep that one
                elif (coda[-1] in {c for oc in onsets for c in [oc[:1], oc]}):
                    keep_for_next = [coda[-1]]
                    coda = coda[:-1]
                    i = j - 1
                else:
                    keep_for_next = []
                    i = j
            else:
                keep_for_next = []
                i = j

            syllables.append("".join(onset + nucleus + coda))

        # Merge stray final consonants only; vowel-final syllables (e.g. *penno → penn.o)
        # must stay separate so the evolver's apocope rule can delete them.
        if len(syllables) >= 2 and len(syllables[-1]) == 1 and syllables[-1] not in self.vowels:
            syllables[-2] += syllables[-1]
            syllables.pop()

        return syllables


# --- quick manual test (mirrors latin.py style) --------------------------------
if __name__ == "__main__":
    pc = PhonoCeltic()

    tests = [
        "*rūskos", "*angʷīnā", "*ɸibeti",
        "RUSKOS", "queti", "guetos", "jowos", "kʷetores",
        "sindos", "eseti", "uksos", "cattā", "ouinos", "āi  āu",
        # convenience: 'f' → ɸ when normalize_f_to_phi=True
        "fibeti"
    ]
    for t in tests:
        w = t.lstrip("*")
        print(f"{t:>12}  →  {pc.to_ipa(w)}")
