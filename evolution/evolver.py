from .ipa_dictionaries import expand_group_keywords, IPA_GROUPS

DEFAULT_IPA_UNITS = sorted([
    # Long/overlong vowels
    'aːː', 'eːː', 'iːː', 'oːː', 'uːː',
    'aː', 'eː', 'iː', 'oː', 'uː',
    # Nasalized variants
    'ã', 'ẽ', 'ĩ', 'õ', 'ũ',
    'ãː', 'ẽː', 'ĩː', 'õː', 'ũː',
    'ãːː', 'ẽːː', 'ĩːː', 'õːː', 'ũːː',
    # Diphthongs
    'ai', 'ei', 'oi', 'au', 'eu', 'ou', 'ae', 'oe', 'ui',
    # Syllabic consonants
    'r̩', 'l̩', 'm̩', 'n̩',
    # Laryngeals
    'h̥', 'h₁̥', 'h₂̥', 'h₃̥',
    # Common affricates
    'tʃ', 'dʒ', 'ts', 'dz',
    # Labialized/aspirated
    'kʷ', 'gʷ', 'pʰ', 'tʰ', 'kʰ', 'bʰ', 'dʰ', 'gʰ',
    # Single IPA characters
] + list("abcdefghijklmnopqrstuvwxyzɪʏʊɛɔæɑɐɶɵøɞɤʌʉɨəː̃ˈˌ"), key=len, reverse=True)

def is_syllable_heavy(syllable_text: str, coda_matters: bool = True) -> bool:
    tokens = tokenize_ipa(syllable_text)

    vowels = IPA_GROUPS.get("ShortVowels", [])
    diphthongs = IPA_GROUPS.get("Diphthongs", [])

    # Rule 1: Long vowel
    if any("ː" in t for t in tokens):
        return True

    # Rule 2: Diphthong
    for i in range(len(tokens) - 1):
        if tokens[i] in vowels and tokens[i + 1] in vowels:
            if tokens[i] + tokens[i + 1] in diphthongs:
                return True

    # Rule 3: Ends in consonant
    if coda_matters and tokens:
        if tokens[-1] not in vowels and tokens[-1] != ".":
            return True

    return False


def tokenize_ipa(ipa_string, ipa_units=DEFAULT_IPA_UNITS):
    """
    Tokenizes an IPA string into linguistically valid phonological units.
    """
    tokens = []
    i = 0
    while i < len(ipa_string):
        for unit in ipa_units:
            if ipa_string.startswith(unit, i):
                tokens.append(unit)
                i += len(unit)
                break
        else:
            tokens.append(ipa_string[i])  # fallback to single char
            i += 1
    return tokens

# ===== WORD-LEVEL CLASSES =====

class Syllable: 
    # Structured container for each syllable
    def __init__(self, text: str, stressed: bool = False):
        self.text = text
        self.stressed = stressed
    
    def __str__(self):
        return f"ˈ{self.text}" if self.stressed else self.text
    
class Word:
    # Encapsulates syllables, original form and syntactic metadata.
    def __init__(self, text: str, syn_func: str = "v"):
        self.original = text
        self.syllables = self.parse_syllables(text)
        self.syn_func = syn_func
        self.history = []

    def get_stress_index(self):
        for i, syll in enumerate(self.syllables):
            if syll.stressed:
                return i
        return None
    

    def log_step(self, rule_name, before, after):
        self.history.append((rule_name, before, after))

    def parse_syllables(self, text: str):
        sylls = text.split(".")
        syllables = []
        for syll in sylls:
            if syll.startswith("ˈ"):
                syllables.append(Syllable(syll[1:], stressed=True))
            else:
                syllables.append(Syllable(syll))
        return syllables
    
    def print_history(self):
        print(f"History for: {self.original}")
        for rule_name, before, after in self.history:
            print(f"  {rule_name:<20}: {before} → {after}")
    
    def to_string(self):
        result = []
        for s in self.syllables:
            try:
                result.append(str(s))
            except Exception as e:
                print(f"[Error] Bad syllable in '{self.original}': {s} ({type(s)}) -> {e}")
                result.append("?")  # visible error marker
        return ".".join(result)
           
# ===== RULE INTERFACE =====

class Rule:
    def __init__(self, raw_data: list):
        self.name = raw_data[0]
        self.type = raw_data[1]
        self.notes = raw_data[2]
        self.params = raw_data[3:] # Rule parameters
    
    def apply(self, word: Word):
        raise NotImplementedError("This rule must implement apply()")

class PhonoRule(Rule):
    def match_stress(self, syll_index, stress_index, stress_solo, skip_stress):
        if skip_stress and syll_index == stress_index:
            return False
        if stress_solo and syll_index != stress_index:
            return False
        return True

    def skip_boundaries_backward(self, phonemes, i):
        while i > 0 and phonemes[i - 1] == ".":
            i -= 1
        return i

    def skip_boundaries_forward(self, phonemes, i):
        while i < len(phonemes) and phonemes[i] == ".":
            i += 1
        return i

    def match_context(self, phonemes, i, old_len, pre_list, post_list):
        i_pre = self.skip_boundaries_backward(phonemes, i)
        i_post = self.skip_boundaries_forward(phonemes, i + old_len)

        pre_ok = any(
            phonemes[i_pre - len(pre):i_pre] == list(pre)
            for pre in pre_list if i_pre >= len(pre)
        ) if pre_list else True

        post_ok = any(
            phonemes[i_post:i_post + len(post)] == list(post)
            for post in post_list if i_post + len(post) <= len(phonemes)
        ) if post_list else True

        return pre_ok and post_ok

    def match_exclusion(self, phonemes, i, old_len, except_pre, except_post):
        i_pre = self.skip_boundaries_backward(phonemes, i)
        i_post = self.skip_boundaries_forward(phonemes, i + old_len)

        pre_hit = any(
            phonemes[i_pre - len(pre):i_pre] == list(pre)
            for pre in except_pre if i_pre >= len(pre)
        ) if except_pre else False

        post_hit = any(
            phonemes[i_post:i_post + len(post)] == list(post)
            for post in except_post if i_post + len(post) <= len(phonemes)
        ) if except_post else False

        return pre_hit or post_hit

    def rebuild_syllables(self, phonemes, stress_index):
        syllables = []
        buffer = []
        syll_index = 0
        for p in phonemes:
            if p == ".":
                if buffer:
                    stressed = (syll_index == stress_index)
                    syllables.append(Syllable("".join(buffer), stressed))
                    buffer = []
                    syll_index += 1
            else:
                buffer.append(p)
        if buffer:
            stressed = (syll_index == stress_index)
            syllables.append(Syllable("".join(buffer), stressed))
        return syllables
    
    def refine_syllables(self, syllables):
        """
        Refines a list of syllables to ensure each contains a valid phonological nucleus.
        - Avoids merging onsets like 'sp', 'sk', 'kl', etc.
        - Prevents merging prosthetic syllables like 'is' with following onset.
        - Rebalances nucleus-only syllables via coda sharing from previous syllable.
        """
        base_vowels = {
            'i', 'y', 'ɨ', 'ʉ', 'ɯ', 'u',
            'ɪ', 'ʏ', 'ʊ',
            'e', 'ø', 'ɘ', 'ɵ', 'ɤ', 'o',
            'e̞', 'ø̞', 'ə', 'ɤ̞', 'o̞',
            'ɛ', 'œ', 'ɜ', 'ɞ', 'ʌ', 'ɔ',
            'æ', 'ɐ',
            'a', 'ɶ', 'ä', 'ɑ', 'ɒ'
        }

        diphthongs = {
            'ai', 'ei', 'oi', 'au', 'eu', 'ou',
            'ae', 'oe', 'ui'
        }

        syllabic_consonants = {
            'r̩', 'l̩', 'm̩', 'n̩', 'h̥', 'h₁̥', 'h₂̥', 'h₃̥'
        }

        # Legal Latin-ish onset clusters
        onset_clusters = {
            'pr', 'br', 'tr', 'dr', 'kr', 'gr', 'fr',
            'pl', 'bl', 'kl', 'gl', 'fl', 'sp', 'st', 'sk',
        }

        nuclei = set()
        for v in base_vowels:
            nuclei.add(v)
            nuclei.add(v + 'ː')
            nuclei.add(v + 'ːː')
            nuclei.add(v + '̃')
            nuclei.add(v + '̃ː')
            nuclei.add(v + '̃ːː')
        nuclei.update(diphthongs)
        nuclei.update(syllabic_consonants)

        def has_nucleus(syllable):
            tokens = tokenize_ipa(syllable.text)
            return any(p in nuclei for p in tokens)

        def starts_with_nucleus(syllable):
            tokens = tokenize_ipa(syllable.text)
            return tokens and tokens[0] in nuclei

        def starts_with_legal_cluster(syllable):
            tokens = tokenize_ipa(syllable.text)
            return len(tokens) >= 2 and tokens[0] + tokens[1] in onset_clusters

        def is_legal_onset(tokens):
            if len(tokens) == 1:
                return True  # single consonant like 's', 'k'
            return tokens[0] + tokens[1] in onset_clusters

        i = 0
        while i < len(syllables):
            curr = syllables[i]

            if has_nucleus(curr):
                # Pull coda from previous if current is a lone nucleus
                tokens = tokenize_ipa(curr.text)
                if len(tokens) == 1 and tokens[0] in nuclei and i > 0:
                    prev = syllables[i - 1]
                    prev_tokens = tokenize_ipa(prev.text)
                    if prev_tokens and prev_tokens[-1] not in nuclei:
                        moved = prev_tokens[-1]
                        prev.text = "".join(prev_tokens[:-1])
                        curr.text = moved + curr.text
                i += 1
                continue

            # MERGE FORWARD: if current has no nucleus, try to merge forward
            if not has_nucleus(curr) and i + 1 < len(syllables):
                next_syll = syllables[i + 1]
                # Prefer merging into syllables starting with nucleus or legal cluster
                next_tokens = tokenize_ipa(next_syll.text)

                # Always merge if next starts with nucleus (nucleus can absorb onset)
                if starts_with_nucleus(next_syll):
                    next_syll.text = curr.text + next_syll.text
                    syllables.pop(i)
                    continue

                # Otherwise: merge only if next does not start with a legal onset
                if not is_legal_onset(next_tokens):
                    next_syll.text = curr.text + next_syll.text
                    syllables.pop(i)
                    continue

            # MERGE BACKWARD: only if current is NOT a legal onset
            curr_tokens = tokenize_ipa(curr.text)
            if i > 0 and not is_legal_onset(curr_tokens):
                syllables[i - 1].text += curr.text
                syllables.pop(i)
                i -= 1
                continue

            i += 1

        
        return syllables

# ===== PHONORULES ====
class AssimilationRule(PhonoRule):
    def __init__(self, raw_data):
        super().__init__(raw_data)
        self.name = raw_data[0]
        self.type = raw_data[1]
        self.notes = raw_data[2]
        self.targets = raw_data[3]  # list of strings
        self.triggers = raw_data[4]  # list of strings
        self.replace = raw_data[5]
        self.regressive = raw_data[6]  # direction: True = reg, False = prog
        self.skip_stress = raw_data[7]

    def apply(self, word):
        # Flatten syllables into list of [syll_index, phoneme, is_stressed]
        phonemes = []
        for i, syll in enumerate(word.syllables):
            tokens = tokenize_ipa(syll.text)
            for t in tokens:
                phonemes.append([i, t, syll.stressed])

        # Determine direction
        start = 0 if self.regressive else 1
        end = len(phonemes) - 1 if self.regressive else len(phonemes)

        for i in range(start, end):
            current = phonemes[i]

            if self.skip_stress and current[2]:
                continue

            neighbor = phonemes[i + 1] if self.regressive else phonemes[i - 1]

            if current[1] in self.targets and neighbor[1] in self.triggers:
                target_index = self.targets.index(current[1])
                current[1] = self.replace[target_index]

        # === Reconstruct syllables by grouping phonemes by syll_index ===
        syllables = []
        current_syll = []
        current_idx = phonemes[0][0] if phonemes else None

        for phoneme in phonemes:
            syll_idx, symbol, stressed = phoneme
            if syll_idx == current_idx:
                current_syll.append(symbol)
            else:
                syllables.append(Syllable("".join(current_syll), stressed=phonemes[phonemes.index(phoneme)-1][2]))
                current_syll = [symbol]
                current_idx = syll_idx

        # Append final syllable
        if current_syll:
            syllables.append(Syllable("".join(current_syll), stressed=phonemes[-1][2]))

        word.syllables = syllables

class DeletionRule(PhonoRule):
    def __init__(self, raw_data):
        super().__init__(raw_data)
        self.name = raw_data[0]
        self.type = raw_data[1]
        self.notes = raw_data[2]
        self.del_list = raw_data[3]
        self.pre_list = raw_data[4] if len(raw_data) > 4 else []
        self.post_list = raw_data[5] if len(raw_data) > 5 else []
        self.except_pre = raw_data[6] if len(raw_data) > 6 else []
        self.except_post = raw_data[7] if len(raw_data) > 7 else []
        self.skip_stress = raw_data[8] if len(raw_data) > 8 else False
        self.stress_solo = raw_data[9] if len(raw_data) > 9 else False

    def apply(self, word: Word):
        # Tokenize syllables
        phonemes = []
        syllable_map = []
        for i, syll in enumerate(word.syllables):
            tokens = tokenize_ipa(syll.text)
            for p in tokens:
                phonemes.append(p)
                syllable_map.append(i)
            phonemes.append(".")
            syllable_map.append(None)
        if phonemes:
            phonemes.pop()
            syllable_map.pop()

        # Stress index
        stress_index = word.get_stress_index()


        edits = []
        i = 0
        while i < len(phonemes):
            syll_idx = syllable_map[i]
            symbol = phonemes[i]

            if symbol not in self.del_list:
                i += 1
                continue

            # Stress filter
            if not self.match_stress(syll_idx, stress_index, self.stress_solo, self.skip_stress):
                i += 1
                continue

            # Context filters
            if not self.match_context(phonemes, i, 1, self.pre_list, self.post_list):
                i += 1
                continue

            if self.match_exclusion(phonemes, i, 1, self.except_pre, self.except_post):
                i += 1
                continue

            edits.append(i)
            i += 1

        # Delete marked phonemes
        for index in reversed(edits):
            phonemes.pop(index)
            syllable_map.pop(index)

        # Rebuild
        rebuilt_syllables = self.rebuild_syllables(phonemes, stress_index)
        word.syllables = self.refine_syllables(rebuilt_syllables)

class DiscontiguousRule(PhonoRule):
    def __init__(self, raw_data):
        super().__init__(raw_data)
        self.name = raw_data[0]
        self.type = raw_data[1]
        self.notes = raw_data[2]
        self.targets = raw_data[3]
        self.triggers = raw_data[4]
        self.replace = raw_data[5]
        self.regressive = raw_data[6]
        self.skip_stress = raw_data[7]
        self.max_distance = raw_data[8]

    def apply(self, word: Word):
        # === Flatten into [syll_index, symbol, is_stressed]
        phonemes = []
        for i, syll in enumerate(word.syllables):
            tokens = tokenize_ipa(syll.text)
            for t in tokens:
                phonemes.append([i, t, syll.stressed])

        # === Identify stress index
        stress_index = word.get_stress_index()


        # === Apply discontiguous assimilation
        for i, current in enumerate(phonemes):
            syll_idx, phoneme, stressed = current

            if phoneme not in self.targets:
                continue
            if self.skip_stress and syll_idx == stress_index:
                continue

            window_indices = self.get_window_indices(phonemes, i, self.max_distance)
            if any(phonemes[j][1] in self.triggers for j in window_indices):
                repl_index = self.targets.index(phoneme)
                current[1] = self.replace[repl_index]

        # === Rebuild syllables
        syllables = []
        current_syll = []
        current_idx = phonemes[0][0] if phonemes else None

        for phoneme in phonemes:
            syll_idx, symbol, stressed = phoneme
            if syll_idx == current_idx:
                current_syll.append(symbol)
            else:
                syllables.append(Syllable("".join(current_syll),
                                          stressed=phonemes[phonemes.index(phoneme) - 1][2]))
                current_syll = [symbol]
                current_idx = syll_idx

        if current_syll:
            syllables.append(Syllable("".join(current_syll), stressed=phonemes[-1][2]))

        word.syllables = syllables

    def get_window_indices(self, phonemes, idx, max_dist):
        indices = []
        dist = 0

        if self.regressive:
            # Look forward (right)
            j = idx + 1
            while j < len(phonemes) and dist < max_dist:
                if phonemes[j][1] != ".":
                    indices.append(j)
                    dist += 1
                j += 1
        else:
            # Look backward (left)
            j = idx - 1
            while j >= 0 and dist < max_dist:
                if phonemes[j][1] != ".":
                    indices.append(j)
                    dist += 1
                j -= 1

        return indices

class EpentheticRule(PhonoRule):
    def __init__(self, rule_data):
        self.name = rule_data[0]
        self.rule_type = rule_data[1]
        self.notes = rule_data[2]
        self.find_list = expand_group_keywords(rule_data[3])
        self.replace_list = rule_data[4]
        self.syllable_pos = rule_data[5]
        self.pre_list = expand_group_keywords(rule_data[6])
        self.post_list = expand_group_keywords(rule_data[7])

    def refine_epenthetic_syllable(self, raw_text: str) -> list:
        if "." in raw_text:
            parts = raw_text.split(".")
            return [Syllable(p) for p in parts if p]
        else:
            return [Syllable(raw_text)]
        
    def apply(self, word: Word):
        if not word.syllables:
            return

        idx = 0 if self.syllable_pos == "first" else -1
        target = word.syllables[idx]
        tokens = tokenize_ipa(target.text)

        new_tokens = []
        modified = False

        for i, tok in enumerate(tokens):
            prev_tok = tokens[i - 1] if i > 0 else ""
            next_tok = tokens[i + 1] if i + 1 < len(tokens) else ""

            if tok in self.find_list:
                pre_ok = not self.pre_list or prev_tok in self.pre_list
                post_ok = not self.post_list or next_tok in self.post_list

                if pre_ok and post_ok:
                    repl_index = self.find_list.index(tok)
                    new_tokens.append(self.replace_list[repl_index])
                    modified = True
                    continue

            new_tokens.append(tok)

        if not modified:
            return

        # Rebuild the modified syllable(s)
        new_text = "".join(new_tokens)
        new_syllables = self.refine_epenthetic_syllable(new_text)

        # Replace the target syllable with new one(s)
        if idx == -1:
            word.syllables = word.syllables[:idx] + new_syllables
        else:
            word.syllables = word.syllables[:idx] + new_syllables + word.syllables[idx+1:]

class ContextualRule(PhonoRule):
    def apply(self, word: Word):
        old_list      = self.params[0]
        new_list      = self.params[1]
        pre_list      = self.params[2] or []
        post_list     = self.params[3] or []
        except_pre    = self.params[4] or []
        except_post   = self.params[5] or []
        skip_stress   = self.params[6] if len(self.params) > 6 else False
        stress_solo   = self.params[7] if len(self.params) > 7 else False

        # Tokenize lists
        old_list = [tokenize_ipa(seq) for seq in old_list]
        new_list = [tokenize_ipa(seq) for seq in new_list]
        pre_list = [tokenize_ipa(seq) for seq in pre_list]
        post_list = [tokenize_ipa(seq) for seq in post_list]
        except_pre = [tokenize_ipa(seq) for seq in except_pre]
        except_post = [tokenize_ipa(seq) for seq in except_post]



        phonemes = []
        syllable_map = []
        for i, syll in enumerate(word.syllables):
            tokens = tokenize_ipa(syll.text)
            for p in tokens:
                phonemes.append(p)
                syllable_map.append(i)
            phonemes.append(".")
            syllable_map.append(None)
        if phonemes:
            phonemes.pop()
            syllable_map.pop()

        stress_index = word.get_stress_index()
        edits = []

        i = 0
        while i < len(phonemes):
            for j, old_seq in enumerate(old_list):
                old_seq_list = list(old_seq)
                end = i + len(old_seq_list)
                if phonemes[i:end] != old_seq_list:
                    continue
                if "." in phonemes[i:end]:
                    continue
                syll_index = syllable_map[i]
                if not self.match_stress(syll_index, stress_index, stress_solo, skip_stress):
                    continue
                if not self.match_context(phonemes, i, len(old_seq_list), pre_list, post_list):
                    continue
                if self.match_exclusion(phonemes, i, len(old_seq_list), except_pre, except_post):
                    continue

                edits.append((i, len(old_seq_list), list(new_list[j])))

            i += 1

        for start, length, replacement in reversed(edits):
            phonemes[start:start+length] = replacement
            
        rebuilt = self.rebuild_syllables(phonemes, stress_index)
        word.syllables = self.refine_syllables(rebuilt)

class SyllabicRule(PhonoRule):
    def apply(self, word: Word):
        old_list = self.params[0]
        new_list = self.params[1]
        position = self.params[2]
        pre_list = self.params[3] if len(self.params) > 3 else []
        post_list = self.params[4] if len(self.params) > 4 else []
        skip_stress = self.params[5] if len(self.params) > 5 else False
        stress_solo = self.params[6] if len(self.params) > 6 else False


        # Resolve position
        if position == "first":
            index = 0
        elif position == "last":
            index = len(word.syllables) - 1
        else:
            try:
                index = int(position)
            except ValueError:
                print(f"[Error] Invalid syllable index: {position}")
                return

        if index < 0 or index >= len(word.syllables):
            print(f"[Warning] Syllable index {index} out of range for word: {word.original}")
            return

        # Build a pseudo-ContextualRule scoped to this syllable
        raw_data = [self.name, "con", self.notes, old_list, new_list, pre_list, post_list, [], [], skip_stress, stress_solo]
        adapter = SyllabicContextAdapter(raw_data, index)
        adapter.apply(word)

        word.syllables = self.refine_syllables(word.syllables)

class SyllabicContextAdapter(ContextualRule):
    def __init__(self, raw_data, syll_index):
        # Force the rule to act *only* on one syllable
        adapted_data = raw_data[:]
        adapted_data[2] += f" (Scoped to syllable {syll_index})"
        self.syll_index = syll_index
        super().__init__(adapted_data)

    def apply(self, word: Word):
        # Slice the syllable, apply rule, reinsert result
        target = word.syllables[self.syll_index]
        subword = Word(target.text)
        subword.syllables[0].stressed = target.stressed

        super().apply(subword)

        # Replace original syllable
        word.syllables[self.syll_index] = subword.syllables[0]

class StressRule(PhonoRule):
    def __init__(self, raw_data):
        super().__init__(raw_data)
        self.name = raw_data[0]
        self.type = raw_data[1]
        self.notes = raw_data[2]
        self.mode = raw_data[3]  # "first", "ultimate", "penult", "antipenult", "weight"

        if self.mode == "weight":
            self.weight_default = raw_data[4]   # fallback: "penult", "first", etc.
            self.weight_window = raw_data[5]    # e.g., 3 for Arabic
            self.coda_matters = raw_data[6] if len(raw_data) > 6 else True
            self.skip_ultimate = raw_data[7] if len(raw_data) > 7 else False

        else:
            self.weight_default = None
            self.weight_window = None
            self.coda_matters = True
            self.skip_ultimate = False

    def apply(self, word: Word):
        sylls = word.syllables
        if not sylls:
            return

        for s in sylls:
            s.stressed = False

        stressed_syll = 0  # fallback default

        if self.mode == "first":
            stressed_syll = 0

        elif self.mode == "ultimate":
            stressed_syll = len(sylls) - 1

        elif self.mode == "penult":
            stressed_syll = len(sylls) - 2 if len(sylls) >= 2 else 0

        elif self.mode == "antipenult":
            stressed_syll = len(sylls) - 3 if len(sylls) >= 3 else 0

        elif self.mode == "weight":
            if len(sylls) == 1:
                stressed_syll = 0
            elif len(sylls) == 2:
                stressed_syll = 0
            else:
                stressed_syll = None
                start = max(0, len(sylls) - self.weight_window)
                end = len(sylls)
                if self.skip_ultimate:
                    end -= 1  # exclude final syllable from search

                for i in range(end - 1, start - 1, -1):
                    if is_syllable_heavy(sylls[i].text, self.coda_matters):
                        stressed_syll = i
                        break

                if stressed_syll is None:
                    if self.weight_default == "penult":
                        stressed_syll = len(sylls) - 2 if len(sylls) >= 2 else 0
                    elif self.weight_default == "ultimate":
                        stressed_syll = len(sylls) - 1
                    elif self.weight_default == "first":
                        stressed_syll = 0
                    elif self.weight_default == "antipenult":
                        stressed_syll = len(sylls) - 3 if len(sylls) >= 3 else 0
                    else:
                        stressed_syll = 0

        if 0 <= stressed_syll < len(sylls):
            sylls[stressed_syll].stressed = True


# ===== EVOLUTION ENGINE ======

class EvolutionEngine:
    def __init__(self, word_texts: list, log_steps: bool = False):
        self.words = [Word(w) for w in word_texts]
        self.rules = []
        self.log_steps = log_steps
        self.rule_cache = {}  # Cache to avoid rebuilding rules

    def apply_rule(self, rule: Rule):
        for word in self.words:
            before = word.to_string()
            rule.apply(word)
            after = word.to_string()

            if self.log_steps and before != after:
                word.log_step(rule.name, before, after)

    def evolve(self, rule_data_list: list):
        for rule_data in rule_data_list:
            rule = self.build_rule(rule_data)
            self.apply_rule(rule)

    def build_rule(self, rule_data: list) -> Rule:
        # Use unmodified rule_data as the cache key
        rule_key = tuple(repr(x) for x in rule_data)

        if rule_key in self.rule_cache:
            return self.rule_cache[rule_key]

        # Expand after checking cache
        expanded_data = rule_data[:3] + [expand_group_keywords(param) for param in rule_data[3:]]
        rule_type = rule_data[1]

        if rule_type == "ass":
            rule = AssimilationRule(expanded_data)
        elif rule_type == "con":
            rule = ContextualRule(expanded_data)
        elif rule_type == "del":
            rule = DeletionRule(expanded_data)
        elif rule_type == "disc":
            rule = DiscontiguousRule(expanded_data)
        elif rule_type == "epen":
            rule = EpentheticRule(expanded_data)
        elif rule_type == "str":
            rule = StressRule(expanded_data)
        elif rule_type == "syll":
            rule = SyllabicRule(expanded_data)
        else:
            raise ValueError(f"Unknown rule type: {rule_type}")

        self.rule_cache[rule_key] = rule
        return rule
