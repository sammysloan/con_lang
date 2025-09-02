import json
from core.phonologizer import Phonologizer


class PhonoLatin(Phonologizer):
    def __init__(self, style = "Classical", debug = False, override_path = None):
        super().__init__(language = "Latin")
        self.style = style
        self.debug = debug
        self.stress_overrides = {}

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
            'qu': 'kʷ', 'ph': "pʰ", 'ch': 'kʰ',
            # Consonants
            'b': 'b', 'c': 'k', 'd': 'd', 'f': 'f', 'g': 'g',
            'h': 'h', 'l': 'l', 'm': 'm', 'n': 'n', 'p': 'p',
            'q': 'k', 'r': 'r', 's': 's', 't': 't', 'v': 'w',
            'x': 'ks', 'z': 'dz',
            # Semi-vowels
            'j': 'j',  # consonantal i
            'y': 'ʏ',  # for Greek loanwords
            # Bugs 
            'ŋ': 'ŋ'
        }

        self.ipa_units = [
            'aː', 'eː', 'iː', 'oː', 'uː',  # long vowels
            'a', 'ɛ', 'ɪ', 'ɔ', 'ʊ',       # short vowels
            'ae', 'au', 'ei', 'oe', 'ui',  # diphthongs
            'kʷ', 'gʷ', 'kʰ', 'pʰ',        # labialized consonants
            'tʃ', 'dz', 'ks',              # affricates and clusters
            'ŋ', 'ʎ', 'ɲ', 'ç',            # nasals and palatals
            'b', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 
            'r', 's', 't', 'v', 'w', 'z',
            'ˈ', ':'
        ]

        self.diphthongs = {'ae', 'au', 'ei', 'oe', 'ui'}
        self.vowels = {'a', 'ɛ', 'ɪ', 'ɔ', 'ʊ', 'e', 'i', 'o', 'u', 'y', 
                    'aː', 'eː', 'iː', 'oː', 'uː', }

    # Parent class overwrites
    def assign_stress(self, syllables):
        """

        """
        enclitic = None
        if syllables[-1] in ('kʷɛ', 'wɛ','nɛ', 'kɛ'):
            enclitic = syllables.pop()

        n = len(syllables)

        # Step 2: Apply stress
        if n == 1:
            syllables[0] = "ˈ" + syllables[0]
        elif n == 2:
            syllables[0] = "ˈ" + syllables[0]
        else:
            penult = syllables[-2]
            if self.is_heavy(penult):
                syllables[-2] = "ˈ" + syllables[-2]
            else:
                syllables[-3] = "ˈ" + syllables[-3]
        
        # Step 3: Reattach enclitic if present
        if enclitic:
            syllables.append(enclitic)

        return syllables

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
        # Step 1: Split orthographic form into phonological units
        units = self.split_into_phonological_units(word)

        # Step 2: Apply contextual phonological rules (e.g., gn → ŋn)
        phonemes = self.apply_context_rules(units)

        # Step 3: Convert to IPA phonemes
        mapped = [self.ipa_map.get(p, p) for p in phonemes] # Rough IPA conversion
        mapped = self.apply_post_mapping_rules(mapped) # Clean up IPA conversion
        ipa_string = "".join(mapped)
        ipa_units = self.tokenize_ipa(ipa_string)

        # Step 4: Syllabify the IPA string
        syllables = self.syllabify(ipa_units)

        # Step 5: Apply stress rules
        stressed_syllables = self.assign_stress(syllables)

        # Step 6: Return final IPA string
        if verbose or self.debug:
            print(f"Word: {word}")
            print(f"  Units:    {units}")
            print(f"  Phonemes: {phonemes}")
            print(f"  Mapped:   {mapped}")
            print(f"  IPA:      {ipa_string}")
            print(f"  Syllables:{syllables}")
            print(f"  Stressed: {stressed_syllables}")
            print("─" * 30)

        return ".".join(stressed_syllables)
       
    # Latin specific rules
    def apply_context_rules(self, phonemes):
        """
        Apply Latin-specific contextual transformation to the IPA phoneme list.
        - Handles consonantal i
        - Handles gn - ŋn
        - Handles geminate consonants
        """

        vowels = {'a', 'e', 'i', 'o', 'u', 'y', 'ā', 'ē', 'ī', 'ō', 'ū'}
        new_phonemes = []
        i = 0 

        # Rule X: convert initial i/u before vowel to j/w
        if len(phonemes) >= 2:
            first = phonemes[0]
            second = phonemes[1]

            if first == 'i' and second in vowels:
                phonemes[0] = 'j'
            elif first == 'u' and second in vowels:
                phonemes[0] = 'w'

        while i < len(phonemes):
            current = phonemes[i]
            next_phon = phonemes[i+1] if i + 1 < len(phonemes) else ""

            # Rule 1: consonantal i → /j/ before vowels
            if current == 'ɪ' and next_phon and next_phon[0] in [
                'a', 'e', 'i', 'o', 'u', 'ʊ', 'ɛ', 'ɪ', 'ɔ']:
                new_phonemes.append("j")
                i += 1
                continue

            # Rule 2: gn → ŋn
            if current == 'g' and next_phon == 'n':
                new_phonemes.append('ŋ')
                new_phonemes.append('n')
                i += 2
                continue

            # Default: add and continue
            new_phonemes.append(current)
            i += 1
            # Break out of for loop 

        return new_phonemes
    
    def apply_post_mapping_rules(self, phonemes):
        """
        Post-mapping IPA adjustments:
        - Tense short vowels [ɛ, ɪ, ʊ, ʏ] to [e, i, u, y] when followed by a vowel
        """
        tense_map = {'ɛ': 'e', 'ɪ': 'i', 'ʊ': 'u', 'ʏ': 'y'}
        ipa_vowels = {'a', 'e', 'i', 'o', 'u', 'y', 'aː', 'eː', 'iː', 'oː', 'uː', 'ae', 'au', 'ei', 'oe', 'ui'}

        result = []
        i = 0
        while i < len(phonemes):
            current = phonemes[i]
            next_ph = phonemes[i+1] if i + 1 < len(phonemes) else ''

            if current in tense_map and next_ph in self.vowels.union(self.diphthongs):
                result.append(tense_map[current])
            else:
                result.append(current)
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

    def is_heavy(self, penult):
        # Step 1: Check for long vowel
        if 'ː' in penult:
            return True
        
        # Step 2: Check for diphthong
        if any(diph in penult for diph in self.diphthongs):
            return True
        

        # Step 3: Check for coda
        final = penult[-1] # Check last character of penult
        if final not in self.vowels:
            return True
        
        return False
    
    def split_into_phonological_units(self, word):
        """
        Split input string into phonological units:
        handles macrons, digraphs (like ae, oe), and preserves long vowels.
        """

        digraphs = ['ae', 'au', 'ei', 'oe', 'ui', 'ch', 'ph', 'qu']
        result = []
        i = 0
        while i < len(word):
            # Check for vowel digraph
            if i + 1 < len(word) and word[i:i+2] in digraphs:
                result.append(word[i: i+2])
                i += 2
            # Handle single character (could be macronized)
            else:
                result.append(word[i])
                i += 1
        return result

    def syllabify(self, units):
        vowels = {'a', 'e', 'i', 'o', 'u', 'ʊ', 'ɪ', 'ɛ', 'ɔ', 'ʏ', 
                'aː', 'eː', 'iː', 'oː', 'uː', 
                'ae', 'au', 'ei', 'oe', 'ui'}
        diphthongs = {'ae', 'au', 'ei', 'oe', 'ui'}
        onset_clusters = {
            'tr', 'dr', 'pr', 'br', 'cr', 'gr', 'fr',
            'pl', 'bl', 'cl', 'gl', 'fl', 'kt', 'pʰ', 'kʰ', 'kʷ'
        }

        print(units)
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

        return syllables

    def tokenize_ipa(self, ipa_string):
        tokens = []
        i = 0
        while i < len(ipa_string):
            match = None
            for unit in sorted(self.ipa_units, key=len, reverse=True):
                if ipa_string[i:i+len(unit)] == unit:
                    match = unit
                    break
            if match:
                tokens.append(match)
                i += len(match)
            else:
                tokens.append(ipa_string[i])
                i += 1
        return tokens
