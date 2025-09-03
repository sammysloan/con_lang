from core.phonologizer import Phonologizer
from evolution.tokenizer import Tokenizer, DEFAULT_IPA_UNITS

class PhonoGermanic(Phonologizer):
    def __init__(self, debug=False, override_path=None):
        super().__init__(language="Proto-Germanic")
        self.debug = debug

        self.tokenizer = Tokenizer(
            units=DEFAULT_IPA_UNITS,
            strict_compounds=False
        )

        self.ipa_map = {
            # Short vowels
            'a': 'ɑ', 'e': 'ɛ', 'i': 'i', 'o': 'ɔ', 'u': 'u',

            # Long vowels
            'ā': 'ɑː', 'ē': 'eː', 'ī': 'iː', 'ō': 'ɔː', 'ū': 'uː',

            # Overlong vowels (circumflexed)
            'â': 'ɑːː', 'ê': 'eːː', 'î': 'iːː', 'ô': 'ɔːː', 'û': 'uːː',

            # Nasal vowels
            'ą': 'ɑ̃', 'ę': 'ɛ̃', 'į': 'ĩ', 'ǫ': 'ɔ̃', 'ų': 'ũ',
            'ą̂': 'ɑ̃ːː', 'ǫ̂': 'ɔ̃ːː',

            # Diphthongs (short)
            'ai': 'ɑi̯', 'au': 'ɑu̯', 'ei': 'ei̯', 'eu': 'eu̯', 'iu': 'iu̯',

            # Diphthongs (long)
            'ōi': 'ɔːi̯', 'ōu': 'ɔːu̯', 'ēi': 'eːi̯', 'ēu': 'eːu̯',

            # Labio-velars
            'kw': 'kʷ', 'gw': 'ɡʷ', 'hw': 'xʷ', 'ƕ': 'xʷ', 

            # Approximants
            'l': 'l', 'r': 'r','j': 'j', 'w': 'w',

            # Fricatives
            'f': 'ɸ', 'þ': 'θ', 'ð': 'ð', 's': 's', 'z': 'z', 'h': 'x', 

            # Stops
            'p': 'p', 'b': 'b', 't': 't', 'd': 'd', 'k': 'k', 'g': 'ɡ',

            # Nasals
            'm': 'm', 'n': 'n',

           # Foreign graphemes as PGmc approximations
            'ph': 'p', 'th': 't', 'ch': 'k', 'qu': 'kʷ', 'ps': 'fs', 'gn':'ŋn',
            'c': 'k', 'v': 'w', 'x': 'ht', 'y': 'i', 'æ': 'a', 'œ': 'e',
        }

        self.ipa_units = [
            # Overlong vowels
            'ɑːː', 'eːː', 'iːː', 'ɔːː', 'uːː',

            # Nasal vowels
            'ɑ̃', 'ɔ̃', 'ɑ̃ː', 'ɔ̃ː', 'ɑ̃ːː', 'ɔ̃ːː',

            # Long vowels
            'ɑː', 'eː', 'iː', 'ɔː', 'uː', 'ɛː',

            # Short vowels
            'ɑ', 'ɛ', 'i', 'ɔ', 'u',

            # Diphthongs
            'ɑi̯', 'ɑu̯', 'eu̯', 'iu̯',
            'ɔːi̯', 'ɔːu̯',
            'ɛːi̯', 'ɛːu̯',

            # Labio-velars
            'kʷ', 'ɡʷ', 'xʷ',

            # Consonants
            'b', 'd', 'f', 'ɡ', 'ɣ', 'β',
            'h', 'k', 'l', 'm', 'n', 'ŋ', 'ŋʷ',
            'p', 'r', 's', 't', 'z', 'θ', 'ð', 'ʍ', 'j', 'w',

            # Stress marker
            'ˈ'
        ]

        self.vowels = {
            'ɑ', 'ɛ', 'i', 'ɔ', 'u',
            'ɑː', 'eː', 'iː', 'ɔː', 'uː',
            'ɑːː', 'eːː', 'iːː', 'ɔːː', 'uːː',
            'ɑ̃', 'ɛ̃', 'ĩ', 'ɔ̃', 'ũ',
            'ɑ̃ːː', 'ɔ̃ːː',
            'ɑi̯', 'ɑu̯', 'ei̯', 'eu̯', 'iu̯', 'ɔːi̯', 'ɔːu̯', 'eːi̯', 'eːu̯'
        }


        self.latinized_vowels = {
            'a', 'e', 'i', 'o', 'u',
            'ā', 'ē', 'ī', 'ō', 'ū',
            'â', 'ê', 'î', 'ô', 'û',
            'ą', 'ę', 'į', 'ǫ', 'ų',
            'ai', 'au', 'ei', 'eu', 'iu', 'oi', 'ui'
        }


 
    # Parent class overwrites
    def assign_stress(self, syllables):
        """
        Proto-Germanic assigns stress to the first syllable of the root.
        In most reconstructions, this is the initial syllable of the word.
        """
        if not syllables:
            return syllables

        # Remove any existing stress marks
        syllables = [syl.lstrip('ˈ') for syl in syllables]

        # Apply stress to the first syllable
        syllables[0] = 'ˈ' + syllables[0]
        return syllables

    def to_ipa(self, word: str) -> str:
        """
        Converts Proto-Germanic orthographic input to IPA
        """
        # 1. Split into phonological units
        units = self.split_into_phonological_units(word)

        # 2. Apply contextual rules (e.g., n → ŋ, g → ɣ)
        phonemes = self.apply_context_rules(units)

        # 3. Convert phonemes to IPA
        mapped = [self.ipa_map.get(p, p) for p in phonemes]

        ipa_string = "".join(mapped)
        ipa_units = self.tokenizer.tokenize(ipa_string)

        # 4. Syllabify the IPA units
        syllables = self.syllabify(ipa_units)
        
        # 5. Assign primary stress marker
        stressed_syllables = self.assign_stress(syllables)

        # 6. Return final IPA string
        if self.debug:
            print(f"Word: {word}")
            print(f"  Units:    {units}")
            print(f"  Phonemes: {phonemes}")
            print(f"  Mapped:   {mapped}")
            print(f"  IPA:      {ipa_string}")
            print(f"  Syllables:{syllables}")
            print(f"  Stressed: {stressed_syllables}")
            print("─" * 30)
        
        return ".".join(stressed_syllables)

    # Proto-Germanic specific methods
    def apply_context_rules(self, phonemes):
        new_phonemes = []

        # === Step 1: TEMP_ unpacking (e.g. ajj → ai̯ + j)
        unpacked = []
        for phon in phonemes:
            if phon == 'TEMP_ajj':
                unpacked.extend(['ai̯', 'j'])
            elif phon == 'TEMP_aww':
                unpacked.extend(['au̯', 'w'])
            elif phon == 'TEMP_eww':
                unpacked.extend(['eu̯', 'w'])
            elif phon == 'TEMP_iww':
                unpacked.extend(['iu̯', 'w'])
            else:
                unpacked.append(phon)

        # === Step 2: Contextual allophones
        i = 0
        while i < len(unpacked):
            current = unpacked[i]
            prev = unpacked[i - 1] if i > 0 else None
            next_ = unpacked[i + 1] if i + 1 < len(unpacked) else None

            # n → ŋ before velars
            if current == 'n' and next_ in {'k', 'g'}:
                new_phonemes.append('ŋ')
                i += 1
                continue

            # n → ŋʷ before labiovelars
            elif current == 'n' and next_ in {'kʷ', 'ɡʷ'}:
                new_phonemes.append('ŋʷ')
                i += 1
                continue

            # b → β between vowels
            elif current == 'b' and prev in self.latinized_vowels and next_ in (self.latinized_vowels | {'w', 'j'}):
                new_phonemes.append('β')
                i += 1
                continue

            # d → ð between vowels
            elif current == 'd' and prev in self.latinized_vowels and next_ in (self.latinized_vowels | {'w', 'j'}):
                new_phonemes.append('ð')
                i += 1
                continue

            # ɡ → ɣ or ɣʷ between vowels
            elif current == 'g' and prev in self.latinized_vowels and next_ in (self.latinized_vowels | {'w', 'j'}):
                next2 = unpacked[i + 2] if i + 2 < len(unpacked) else ""
                if next_ == 'w':
                    new_phonemes.append('ɣʷ')
                    i += 1
                    continue
                else:
                    new_phonemes.append('ɣ')
                    i += 1
                    continue

            # Default
            else:
                new_phonemes.append(current)
                i += 1

        return new_phonemes

    def get_digraphs(self):
        return {
        # Native diphthongs
        'ai', 'au', 'ei', 'eu', 'iu',
        'ōi', 'ōu', 'ēi', 'ēu',

        # Native labio-velars
        'kw', 'gw', 'hw', 'ƕ',

        # Non-native / foreign digraphs
        'qu', 'ph', 'ch', 'th', 'ps', 'gn' }
    
    def split_into_phonological_units(self, word):
        # Normalize compound glide clusters
        special_clusters = {
            'ajj': 'TEMP_ajj',
            'aww': 'TEMP_aww',
            'eww': 'TEMP_eww',
            'iww': 'TEMP_iww'
        }

        result = []
        i = 0
        while i < len(word):
            tri = word[i:i+3]
            if tri in special_clusters:
                result.append(special_clusters[tri])
                i += 3
            else:
                # Fallback to digraph recognition
                if i + 1 < len(word) and word[i:i+2] in self.get_digraphs():
                    result.append(word[i:i+2])
                    i += 2
                else:
                    result.append(word[i])
                    i += 1
        return result

    def syllabify(self, units):
        vowels = self.vowels
        onset_clusters = {
            'tr', 'dr', 'pr', 'br', 'kr', 'gr', 'fr',
            'pl', 'bl', 'kl', 'gl', 'fl',
            'sp', 'st', 'sk'
        }

        syllables = []
        i = 0
        n = len(units)

        while i < n:
            onset = []
            nucleus = []

            while i < n and units[i] not in vowels:
                onset.append(units[i])
                i += 1

            if i < n:
                nucleus.append(units[i])
                i += 1

            j = i
            consonants = []
            while j < n and units[j] not in vowels:
                consonants.append(units[j])
                j += 1

            if len(consonants) == 0:
                syllables.append("".join(onset + nucleus))
                i = j

            elif len(consonants) == 1:
                if j < n and units[j] in vowels:  # check for next vowel
                    syllables.append("".join(onset + nucleus))
                    i = j - len(consonants)  # re-parse the consonant as onset
                else:
                    syllables.append("".join(onset + nucleus + [consonants[0]]))
                    i += 1

            elif len(consonants) >= 2 and "".join(consonants[1:3]) in onset_clusters:
                syllables.append("".join(onset + nucleus + [consonants[0]]))
                i += 1

            else:
                syllables.append("".join(onset + nucleus + [consonants[0]]))
                i += 1

        if len(syllables) >= 2 and len(syllables[-1]) == 1:
            if syllables[-1] not in vowels:
                syllables[-2] += syllables[-1]
                syllables.pop()

        if self.debug:
            print(f"Syllables: {syllables}")
        return syllables
    
