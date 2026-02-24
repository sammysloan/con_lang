import json

try:
    # when running as a package (recommended)
    from core.phonologizer import Phonologizer
except ModuleNotFoundError:
    # when running directly from core/
    from phonologizer import Phonologizer

from evolution import evolver as _evo
from evolution.tokenizer import Tokenizer, DEFAULT_IPA_UNITS

from evolution.ipa_dictionaries import IPA_GROUPS

LATIN_DIPHTHONGS = {"ae", "au", "ei", "oe", "ui"}

class PhonoLatin(Phonologizer):
    def __init__(self, style = "Classical", debug = False, override_path = None):
        super().__init__(language = "Latin")

        self.style = style
        self.debug = debug
        self.stress_overrides = {}
        _evo.set_weight_fn(self.is_syllable_heavy)

        if override_path:
            try:
                with open(override_path, encoding="utf-8") as f:
                    self.stress_overrides = json.load(f)
            except FileNotFoundError:
                print(f"[Warning] Stress override file not found: {override_path}")
            except json.JSONDecodeError:
                print(f"[Error] Malformed JSON in: {override_path}")

        self.ipa_map = {
            # Short vowels
            'a': 'a', 'e': 'ɛ', 'i': 'ɪ', 'o': 'ɔ', 'u': 'ʊ',
            # Long vowels (macrons)
            'ā': 'aː', 'ē': 'eː', 'ī': 'iː', 'ō': 'oː', 'ū': 'uː',
            # Diphthongs (Classical Latin)
            'ae': 'ae', 'au': 'au', 'ei': 'ei', 'oe': 'oe', 'ui': 'ui',
            # Other digraphs
            'qu': 'kʷ', 'gu': 'ɡʷ','ph': "pʰ", 'ch': 'kʰ',
            # Consonants
            'b': 'b', 'c': 'k', 'd': 'd', 'f': 'f', 'g': 'ɡ',
            'h': 'h', 'l': 'l', 'm': 'm', 'n': 'n', 'p': 'p',
            'q': 'k', 'r': 'r', 's': 's', 't': 't', 'v': 'w',
            'x': 'ks', 'z': 'dz',
            # Semi-vowels
            'j': 'j',  # consonantal i
            'y': 'ʏ',  # for Greek loanwords
            # Bugs 
            'ŋ': 'ŋ'
        }


        # Latin-stage diphthongs you want to count as one nucleus in strict mode
        self.diphthongs = set(LATIN_DIPHTHONGS)

        # A robust vowel set in IPA space (short, long, overlong); handles your ɪ/ʊ/ɛ cases too
        shorts = set(IPA_GROUPS.get("ShortVowels", []))
        self.vowels = (
            shorts
            | {v + "ː" for v in shorts}
            | {v + "ːː" for v in shorts}
        )

        # (optional) if you sometimes see nasalized vowels during mapping
        self.vowels |= {v + "̃" for v in shorts} | {v + "̃ː" for v in shorts} | {v + "̃ːː" for v in shorts}

        # === Tokenizer wiring (STRICT at base stage) ===
        self.legal_units = None  # you can give a curated Latin-stage inventory later
        self.legal_compounds = set(LATIN_DIPHTHONGS) | {"kʷ", "ɡʷ", "r̩", "l̩", "m̩", "n̩"}

        self.tokenizer = Tokenizer(
            units=DEFAULT_IPA_UNITS,
            legal_units=self.legal_units,
            legal_compounds=self.legal_compounds,
            strict_compounds=True,
        )


    # Parent class overwrites
    def assign_stress(self, syllables):
        """

        """
        if not syllables: 
            return syllables # Avoid index crash from blank words
        
        enclitic_tail = {'kʷɛ', 'wɛ', 'nɛ', 'kɛ'}  # -que, -ve, -ne, -ce
        enclitic = None

        # Only detach an enclitic if there’s something to cling to
        if syllables[-1] in enclitic_tail:
            if len(syllables) == 1:
                # Standalone enclitic: pick a safe default and bail
                syllables[0] = 'ˈ' + syllables[0]   # or just `return syllables` if you prefer no stress on clitics
                return syllables
        
            enclitic = syllables.pop()


        n = len(syllables)

        # Step 2: Apply stress
        if n == 1:
            syllables[0] = "ˈ" + syllables[0]
        elif n == 2:
            syllables[0] = "ˈ" + syllables[0]
        else:
            penult = syllables[-2]
            if self.is_syllable_heavy(penult, coda_matters=True):
                syllables[-2] = "ˈ" + syllables[-2]
            else:
                syllables[-3] = "ˈ" + syllables[-3]
        
        # Step 3: Reattach enclitic if present
        if enclitic:
            syllables.append(enclitic)

        return syllables


    def is_syllable_heavy(self, syllable_text: str, coda_matters: bool = True) -> bool:
        """
        Latin heaviness:
        - long/overlong/nasalized-long nucleus (contains 'ː') → heavy
        - diphthong nucleus (ae, au, oe, ei, ui) → heavy
        - closed syllable (final token not a vowel) → heavy if coda_matters
        """
        toks = _evo.tokenize_ipa(syllable_text)
        if not toks:
            return False

        # long/overlong (and nasalized-long) vowels
        if any("ː" in t for t in toks):
            return True

        # diphthong nucleus (your pipeline tokenizes these as single units)
        if any(t in self.diphthongs for t in toks):
            return True

        # coda consonant ⇒ heavy, if we care about codas
        if coda_matters:
            if toks[-1] not in self.vowels:
                return True

        return False


        
    def to_ipa(self, word: str, use_override: bool = True, verbose: bool = False) -> str:
        """
        Convert a Latin word in orthographic form to IPA with proper syllabification and stress.

        Parameters:
            word (str): The original Latin word (e.g., 'magnus').
            use_override (bool): If True, use stress overrides from dictionary when available.
            verbose (bool): If True, print debug information during transformation.

        Returns:
            str: The IPA transcription with stress and syllable boundaries (e.g., 'ˈmaŋ.nʊs').
        """

        def _coalesce_length(units):
            out = []
            for u in units:
                if (
                    u == LENGTH
                    and out
                    and out[-1] in VOWELS
                    and LENGTH not in out[-1]
                ):
                    out[-1] = out[-1] + LENGTH
                else:
                    out.append(u)
            return out

        # 0) Optional stress overrides (case‑insensitive convenience)
        if use_override and self.stress_overrides:
            for k in (word, word.capitalize(), word.upper()):
                if k in self.stress_overrides:
                    override_syllables = list(self.stress_overrides[k])
                    if verbose or self.debug:
                        print(f"[override] {word} -> {override_syllables}")
                    return ".".join(override_syllables)

        # 1) Split orthographic string into phonological units (your existing method)
        units = self.split_into_phonological_units(word)

        # 2) Apply Latin‑specific contextual rules on those units (your existing method)
        phonemes = self.apply_context_rules(units)

        # 3) Map to IPA using your ipa_map, then post‑mapping cleanups (your existing methods)
        mapped = [self.ipa_map.get(p, p) for p in phonemes]
        mapped = self.apply_post_mapping_rules(mapped)
        ipa_string = "".join(mapped)

        VOWELS = {'a','e','i','o','u','y'}
        LENGTH = 'ː'


        # print("DEBUG quod tokens:", self.tokenizer.tokenize(ipa_string))

        # 4) Syllabify the token list (your existing method expects tokens)
        tokens = self.tokenizer.tokenize(ipa_string)
        tokens = _coalesce_length(tokens)       # << ADD THIS LINE
        syllables = self.syllabify(tokens)

        # 5) Stress assignment (your existing method)
        stressed_syllables = self.assign_stress(syllables)

        # 6) Debug printout (kept identical in spirit to your current version)
        if verbose or self.debug:
            print(f"Word: {word}")
            print(f"  Units:    {units}")
            print(f"  Phonemes: {phonemes}")
            print(f"  Mapped:   {mapped}")
            print(f"  IPA:      {ipa_string}")
            print(f"  Syllables:{syllables}")
            print(f"  Stressed: {stressed_syllables}")
            print("─" * 30)

        # 7) Return final string
        return ".".join(stressed_syllables)

    # Latin specific rules
    def apply_context_rules(self, phonemes):
        """
        Apply Latin-specific contextual transforms on **orthographic** units:
        - initial i/u + vowel → j/w
        - i + vowel (medial)  → j
        - gn → ŋn (so that 'agnus' → aŋ.nus after mapping)
        """
        vowels = {'a', 'e', 'i', 'o', 'u', 'y', 'ā', 'ē', 'ī', 'ō', 'ū'}
        new = []
        i = 0

        # Initial i/u → j/w before vowel
        if len(phonemes) >= 2:
            first, second = phonemes[0], phonemes[1]
            if first == 'i' and second in vowels:
                phonemes[0] = 'j'
            elif first == 'u' and second in vowels:
                phonemes[0] = 'w'

        while i < len(phonemes):
            cur = phonemes[i]
            nxt = phonemes[i + 1] if i + 1 < len(phonemes) else ""
            prev = phonemes[i - 1] if i - 1 >= 0 else ""

            # Only glide if i is between vowels (V_i_V)
            if cur == 'i' and nxt in vowels and prev in vowels:
                new.append('j')
                i += 1
                continue

            # gn → ŋn (orthographic trigger; IPA mapping will keep ŋ)
            if cur == 'g' and nxt == 'n':
                new.append('ŋ'); new.append('n')
                i += 2
                continue

            # n → ŋ before velars (g, gu)
            if cur == 'n' and nxt in ('g', 'gu'):
                new.append('ŋ')
                i += 1
                continue

            new.append(cur)
            i += 1

        return new

    def apply_post_mapping_rules(self, phonemes):
        """
        Post‑mapping IPA adjustments (after orthography→IPA mapping, before tokenization).
        """
        tense_map = {'ɛ': 'e', 'ɪ': 'i', 'ʊ': 'u', 'ʏ': 'y'}

        result = []
        i = 0
        while i < len(phonemes):
            cur = phonemes[i]
            nxt = phonemes[i + 1] if i + 1 < len(phonemes) else ''

            # If the current segment is a lax short vowel and the next segment is any vowel
            # (monophthong or diphthong), tense it.
            if cur in tense_map and (nxt in self.vowels or nxt in self.diphthongs):
                result.append(tense_map[cur])
            else:
                result.append(cur)

            i += 1

        return result

    def debug_syllable(self, original, is_stressed, units, mapped, final):
        if not self.debug:
            return # Don't print if debug is off
        
        print(f"Syllable: {original}")
        print(f"  Stressed: {'Yes' if is_stressed else 'No'}")
        print(f"  Units:    {units}")
        print(f"  Mapped:   {mapped}")
        print(f"  Final:    {final}")
        print("─" * 30)

    def split_into_phonological_units(self, word):
        """
        Split orthography into phonological units.
        - Treat ae, au, oe as true diphthongs everywhere.
        - Treat ei/ui as diphthongs by default, *except* when a vowel follows
        (so 'eius', 'cuius', 'huius' split to e+i before the next vowel).
        - Keep common digraphs (ch, ph, qu) as single units.
        """

        digraphs = {'ae', 'au', 'ei', 'oe', 'ui', 'ch', 'ph', 'gu', 'qu'}
        vowels_orth = set('aeiouyāēīōū')  # main.py lowercases input already

        result = []
        i = 0
        n = len(word)

        while i < n:
            # Try a digraph
            if i + 1 < n:
                pair = word[i:i+2]

                # if pair is 'gu' and the next char isn't a vowel, don't treat as digraph
                if pair == 'gu':
                    nxt = word[i+2] if i + 2 < n else ''
                    if not nxt or nxt not in vowels_orth:
                        result.append(word[i])  # 'g'
                        i += 1                  # leave 'u' for next loop
                        continue

                if pair in digraphs:
                    # Look one more char ahead to decide ei/ui behavior
                    nxt = word[i+2] if i + 2 < n else ''
                    if pair in ('ei', 'ui') and nxt in vowels_orth:
                        # Split: keep the first letter now; 'i' is handled next loop
                        result.append(word[i])   # 'e' or 'u'
                        i += 1                   # leave 'i' for next iteration
                        continue
                    # Otherwise keep the digraph together
                    result.append(pair)
                    i += 2
                    continue

            # Fallback: single char (covers macronized vowels too)
            result.append(word[i])
            i += 1

        return result

    def syllabify(self, units):
        
        diphthongs = self.diphthongs
        onset_clusters = {
        'tr', 'dr', 'pr', 'br', 'cr', 'ɡr', 'fr',
        'pl', 'bl', 'cl', 'ɡl', 'fl', 'pʰ', 'kʰ', 'kʷ', 'gʷ'
        }
        vowels = {'a', 'e', 'i', 'o', 'u', 'ʊ', 'ɪ', 'ɛ', 'ɔ', 'ʏ', 
                'aː', 'eː', 'iː', 'oː', 'uː', 
                'ae', 'au', 'ei', 'oe', 'ui'
        }


        syllables = []
        i = 0
        n = len(units) # number of chars in word

        while i < n:
            onset = []
            nucleus = []
            consonants = []

            # Step 1: onset
                # Add prevowel consonants to onset
            while i < n and units[i] not in vowels:
                onset.append(units[i])
                i += 1

            # Step 2: nucleus
                # Add vowel to nucleus
            if i < n and units[i] in vowels:
                nucleus.append(units[i])

                i += 1
                # Check for non-diphthong second vowel (i.e. "glo.ri.a")
                if i < n and units[i] in vowels and units[i-1] + units[i] not in diphthongs:
                    # Commit current syll and continue from next vowel
                    syllables.append("".join(onset + nucleus))
                    onset = []
                    nucleus = [units[i]]

                    i += 1

            # Step 3: look ahead for post-vowel consonants
            j = i
            while j < n and units[j] not in vowels:
                consonants.append(units[j])
                j += 1

            # Step 4: syllable boundary logic
                # A) Special case: [ŋ, n] cluster
            if consonants[:2] == ['ŋ', 'n']:
                syllables.append("".join(onset + nucleus + ['ŋ']))

                i += 1
                continue
                
                # B) No consonants
            elif len(consonants) == 0:
                syllables.append("".join(onset + nucleus))
                i = j  # advance to end
            
                # C) Single consonant - begins new syll
            elif len(consonants) == 1:
                syllables.append("".join(onset + nucleus))
                j = i # Single consonant never acts as coda
            
                # D) Check for legal consonant clusters
            elif "".join(consonants[:2]) in onset_clusters:
                syllables.append("".join(onset + nucleus))
                j = i + 2 # Begins new syll with legal cluster
            
                # E) Split illegal cluster
            else:
                syllables.append("".join(onset + nucleus + consonants[:1]))

                i += 1
                j = i + 1 # Split cluster, begins new syll with con at 1

        # Merge any 1-char orphan syllables at end
        if len(syllables) >= 2 and len(syllables[-1]) == 1:
            if syllables[-1] not in vowels:
                syllables[-2] += syllables[-1]
                syllables.pop()

        # Merge split monosyllables caused by final consonant clusters
        if len(syllables) == 2 and all(c not in 'aeiouɛɪʊɔʏ' for c in syllables[1]):
            syllables[0] += syllables[1]
            syllables.pop()

        print(f"[Latin:syllables] -> {syllables}")
        return syllables

