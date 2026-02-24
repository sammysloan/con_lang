from typing import Callable
from .ipa_dictionaries import expand_group_keywords, IPA_GROUPS
from .tokenizer import Tokenizer, DEFAULT_IPA_UNITS

# Sonority helpers (soft, language-agnostic)
_SONORITY = {
    "stops": {"p","b","t","d","k","ɡ","q","ʔ","c","ɟ","ʈ","ɖ"},
    "fric":  {"f","v","θ","ð","s","z","ʃ","ʒ","ɸ","β","x","ɣ","ç","ʝ","χ","ʁ","h"},
    "nasal": {"m","n","ɲ","ŋ","ɱ"},
    "liquid":{"l","r","ɾ"},
    "glide": {"j","w","ɥ","ɰ"},
}
def _sonority_rank(seg: str) -> int:
    if seg in _SONORITY["stops"]:  return 1
    if seg in _SONORITY["fric"]:   return 2
    if seg in _SONORITY["nasal"]:  return 3
    if seg in _SONORITY["liquid"]: return 4
    if seg in _SONORITY["glide"]:  return 5
    return 2  # safe default: treat unknowns like fricatives

def _cluster_policy_decision(position, syll_idx, n_sylls, cons_seq, rule):
    if not cons_seq:
        return None

    scope = _scope_for_index(syll_idx, n_sylls)
    if rule.position not in (position, "any"):
        return None
    if rule.scope not in (scope, "any"):
        return None

    tup = tuple(cons_seq)
    maxL = rule.max_check
    allow = getattr(rule, "allow_set", set())
    ban = getattr(rule, "ban_set", set())

    matched_allow = any(tuple(tup[:L]) in allow for L in range(2, min(maxL, len(tup)) + 1))
    if matched_allow:
        return True

    matched_ban = any(tuple(tup[:L]) in ban for L in range(2, min(maxL, len(tup)) + 1))
    if matched_ban:
        return False

    return None


def _licensable_onset(tokens: list[str]) -> bool:
    # s-cluster exception: s + stop (+ liquid/glide) is OK
    if tokens and tokens[0] == "s":
        if len(tokens) == 1: return True
        if tokens[1] in _SONORITY["stops"]:
            if len(tokens) == 2: return True
            if len(tokens) == 3 and (tokens[2] in _SONORITY["liquid"] or tokens[2] in _SONORITY["glide"]):
                return True
    # general SSP: sonority left→right
    ranks = [_sonority_rank(t) for t in tokens]
    return all(ranks[i] <= ranks[i+1] for i in range(len(ranks)-1))


def _scope_for_index(i: int, n: int) -> str:
    if i == 0: return "word_initial"
    if i == n - 1: return "word_final"
    return "word_medial"

def _onset_tokens(tokens: list[str], nuclei: set[str]) -> list[str]:
    onset = []
    for t in tokens:
        if t in nuclei:
            break
        onset.append(t)
    return onset

def _coda_tokens(tokens: list[str], nuclei: set[str]) -> list[str]:
    # everything after the last nucleus
    last_nuc = -1
    for j, t in enumerate(tokens):
        if t in nuclei:
            last_nuc = j
    return tokens[last_nuc+1:] if last_nuc >= 0 else tokens

def _prep_ctx_list(seq_list):
    out = []
    for s in (seq_list or []):
        if s == "*Blank":
            out.append(["*Blank"]) 
        else:
            out.append(tokenize_ipa(s))
    return out


# One module-level tokenizer (permissive by default for evolution stage)
_TOK = Tokenizer(units=DEFAULT_IPA_UNITS, strict_compounds=False)

def tokenize_ipa(ipa_string):
    return _TOK.tokenize(ipa_string)

# Language specific weight function (optional)
_WEIGHT_FN: Callable[[str, bool], bool] | None = None

def set_weight_fn(fn: Callable[[str, bool], bool] | None) -> None:
    """Languages can register a custom heaviness function. Pass None to reset."""
    global _WEIGHT_FN
    _WEIGHT_FN = fn

def is_syllable_heavy(syllable_text: str, coda_matters: bool = True) -> bool:
    """Delegates to a language-supplied function if present; otherwise uses a safe generic fallback."""
    if _WEIGHT_FN is not None:
        return _WEIGHT_FN(syllable_text, coda_matters)

    # --- Generic fallback (very conservative) ---
    toks = tokenize_ipa(syllable_text)
    vowels = set(IPA_GROUPS.get("ShortVowels", []))
    # long vowel nucleus
    if any("ː" in t for t in toks):
        return True
    
    # coda consonant
    if coda_matters and toks:
        last = toks[-1]
        if last not in vowels and last not in {"i̯", "u̯", "."}:
            return True
        
    return False

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
    def __init__(self, raw_data):
        super().__init__(raw_data)
        self.cluster_policies = []

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
        def _pre_anchor(pre_seq):
            if pre_seq and pre_seq[-1] == ".":
                return i  # look immediately before i, boundary-inclusive
            return self.skip_boundaries_backward(phonemes, i)

        def _post_anchor(post_seq):
            if post_seq and post_seq[0] == ".":
                return i + old_len  # look immediately after match, boundary-inclusive
            return self.skip_boundaries_forward(phonemes, i + old_len)

        pre_ok = True
        if pre_list:
            pre_ok = False
            for pre in pre_list:
                if pre == ["*Blank"]:
                    if i == 0 or phonemes[i - 1] == ".":
                        pre_ok = True
                        break

                anchor = _pre_anchor(pre)
                if anchor >= len(pre) and phonemes[anchor - len(pre):anchor] == list(pre):
                    pre_ok = True
                    break

        post_ok = True
        if post_list:
            post_ok = False
            for post in post_list:
                if post == ["*Blank"]: 
                    if i + old_len >= len(phonemes) or phonemes[i + old_len] == ".":
                        post_ok = True
                        break

                anchor = _post_anchor(post)
                if anchor + len(post) <= len(phonemes) and phonemes[anchor:anchor + len(post)] == list(post):
                    post_ok = True
                    break
        
        return pre_ok and post_ok

    def match_exclusion(self, phonemes, i, old_len, except_pre, except_post):
        def _pre_anchor(pre_seq):
            if pre_seq and pre_seq[-1] == ".":
                return i
            return self.skip_boundaries_backward(phonemes, i)

        def _post_anchor(post_seq):
            if post_seq and post_seq[0] == ".":
                return i + old_len
            return self.skip_boundaries_forward(phonemes, i + old_len)

        pre_hit = False
        if except_pre:
            for pre in except_pre:
                anchor = _pre_anchor(pre)
                if anchor >= len(pre) and phonemes[anchor - len(pre):anchor] == list(pre):
                    pre_hit = True
                    break

        post_hit = False
        if except_post:
            for post in except_post:
                anchor = _post_anchor(post)
                if anchor + len(post) <= len(phonemes) and phonemes[anchor:anchor + len(post)] == list(post):
                    post_hit = True
                    break

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
        - Uses sonority sequencing to prevent illegal onset merges.
        - Prevents merging prosthetic syllables with following onset.
        - Rebalances nucleus-only syllables via coda sharing from previous syllable.
        """

        nuclei = set(IPA_GROUPS.get("Nuclei", []))
        short_vowels = set(IPA_GROUPS.get("ShortVowels", []))  # for a tiny safety fallback

        def has_nucleus(syllable):
            toks = tokenize_ipa(syllable.text)
            if any(t in nuclei for t in toks):
                return True
            # belt-and-suspenders: vowel + combining tilde split as separate tokens
            return any(i + 1 < len(toks) and toks[i] in short_vowels and toks[i + 1] == "̃"
                    for i in range(len(toks)))

        def starts_with_nucleus(syllable):
            toks = tokenize_ipa(syllable.text)
            if not toks:
                return False
            if toks[0] in nuclei:
                return True
            # also treat leading vowel + combining tilde as a nucleus-start
            return len(toks) >= 2 and toks[0] in short_vowels and toks[1] == "̃"

        i = 0
        while i < len(syllables):
            curr = syllables[i]

            if has_nucleus(curr):
                # If current syllable is just a nucleus token, borrow previous coda as onset.
                toks = tokenize_ipa(curr.text)
                if len(toks) == 1 and (toks[0] in nuclei or (toks[0] in short_vowels)) and i > 0:
                    prev = syllables[i - 1]
                    prev_toks = tokenize_ipa(prev.text)
                    if prev_toks and prev_toks[-1] not in nuclei:
                        moved = prev_toks[-1]
                        prev.text = "".join(prev_toks[:-1])
                        curr.text = moved + curr.text
                i += 1
                continue


            # MERGE FORWARD: if current has no nucleus, try to merge into the next syllable
            if i + 1 < len(syllables):
                nxt = syllables[i + 1]
                nxt_toks = tokenize_ipa(nxt.text)
                onset = _onset_tokens(nxt_toks, nuclei)


                policy_dec = None
                for rule in self.cluster_policies:
                    d = _cluster_policy_decision("onset", i+1, len(syllables), onset, rule)
                    if d is not None:
                        policy_dec = d

                if policy_dec is False:
                    pass
                elif policy_dec is True:
                    nxt.text = curr.text + nxt.text
                    syllables.pop(i)
                    continue

                # If next starts with a nucleus, absorb curr into it.
                if starts_with_nucleus(nxt):
                    nxt.text = curr.text + nxt.text
                    syllables.pop(i)
                    continue

                # Otherwise: only merge if the next onset is NOT licensable by SSP (incl. s-cluster exception).
                if not _licensable_onset(nxt_toks):
                    nxt.text = curr.text + nxt.text
                    syllables.pop(i)
                    continue


            # A syllable with no nucleus may not stand alone.
            if not has_nucleus(curr):
                # Prefer attaching forward (as onset) if a next syllable exists
                if i + 1 < len(syllables):
                    syllables[i + 1].text = curr.text + syllables[i + 1].text
                    syllables.pop(i)
                    continue
                # Otherwise, attach backward (as coda) if a previous syllable exists
                if i > 0:
                    syllables[i - 1].text += curr.text
                    syllables.pop(i)
                    i -= 1
                    continue
                # If it's the only syllable, nothing to merge with — just leave it.

            # MERGE BACKWARD: if curr isn't a licensable onset, attach it to the previous syllable
            curr_toks = tokenize_ipa(curr.text)
            if i > 0 and not _licensable_onset(curr_toks):
                syllables[i - 1].text += curr.text
                syllables.pop(i)
                i -= 1
                continue

            # ==== INSERT: ClusterPolicy for CURRENT CODA ====
            curr_toks = tokenize_ipa(curr.text)
            coda = _coda_tokens(curr_toks, nuclei)

            policy_dec = None
            for rule in self.cluster_policies:
                d = _cluster_policy_decision("coda", i, len(syllables), coda, rule)
                if d is not None:
                    policy_dec = d

            if policy_dec is False and i + 1 < len(syllables) and coda:
                # Coda explicitly banned → push one consonant forward
                last = coda[-1]
                # Remove the last token's literal slice; this assumes tokens are single-codepoint strings
                curr.text = curr.text[:-len(last)]
                syllables[i + 1].text = last + syllables[i + 1].text
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
        self.require_identical = raw_data[8] if len(raw_data) > 8 else False


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

            # Geminate check
            if self.require_identical:
                if current[1] != neighbor[1]:
                    continue

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
    nuclei = set(IPA_GROUPS.get("Nuclei", [])) | set(IPA_GROUPS.get("ShortVowels", []))
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
        self.sonority_safe = raw_data[10] if len(raw_data) > 10 else True

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

        pre_list_tok    = _prep_ctx_list(self.pre_list)
        post_list_tok   = _prep_ctx_list(self.post_list)
        except_pre_tok  = _prep_ctx_list(self.except_pre)
        except_post_tok = _prep_ctx_list(self.except_post)



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
            if not self.match_context(phonemes, i, 1, pre_list_tok, post_list_tok):
                i += 1
                continue

            if self.match_exclusion(phonemes, i, 1, except_pre_tok, except_post_tok):
                i += 1
                continue

            # -- Sonority guard (optional) --
            if self.sonority_safe:
                # Bold the onset starting at the boundary to the right of the deletion
                j = i + 1
                onset = []
                # Treat any token in Nuclei (or with ː) as a vowel-ish boundary
                while j < len(phonemes) and phonemes[j] != "." and phonemes[j] not in self.nuclei and "ː" not in phonemes[j]:
                    onset.append(phonemes[j])
                    if len(onset) >= 3: break   # 2–3 is enough for the check
                    j += 1

                if not _licensable_onset(onset):
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
        self.require_identical = raw_data[11] if len(raw_data) > 12 else False



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

class ClusterPolicyRule(PhonoRule):
    """
    A non-transformational rule that constrains legal consonant clusters
    for onsets and codas. Does not modify words directly.
    Instead, its parameters are consumed by the syllabifier.
    """

    def __init__(self, data):
        super().__init__(data)
        # Expected data format from preset_edit:
        # [name, "clp", notes, position, scope, allow, ban, max_check]
        self.name = data[0]
        self.rule_type = data[1]
        self.notes = data[2]
        self.position = data[3]
        self.scope = data[4]
        self.allow = [tuple(c) for c in (data[5] or [])]
        self.ban   = [tuple(c) for c in (data[6] or [])]
        self.max_check = int(data[7]) if len(data) > 7 else 3

        # Precompute lookup sets for speed
        self.allow_set = set(self.allow)
        self.ban_set   = set(self.ban)

    def apply(self, word_obj):
        """
        ClusterPolicy does not transform the word directly.
        We simply return it unchanged.
        """
        return word_obj

    def to_dict(self):
        """Optional: convenience for serialization."""
        return {
            "type": "ClusterPolicy",
            "position": self.position,
            "scope": self.scope,
            "allow": [list(c) for c in self.allow],
            "ban": [list(c) for c in self.ban],
            "max_check": self.max_check,
        }

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
        old_list    = [tokenize_ipa(seq) for seq in old_list]
        new_list    = [tokenize_ipa(seq) for seq in new_list]
        pre_list    = _prep_ctx_list(pre_list)
        post_list   = _prep_ctx_list(post_list)
        except_pre  = _prep_ctx_list(except_pre)
        except_post = _prep_ctx_list(except_post)



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
        
        # --- NEW: if the scoped edit deleted the syllable entirely, drop it
        if not subword.syllables or all(s.text == "" for s in subword.syllables):
            was_stressed = target.stressed
            # remove the empty syllable
            del word.syllables[self.syll_index]
            # if we just deleted the stressed syllable, pass stress to a neighbor
            if was_stressed and word.syllables:
                handoff = min(self.syll_index, len(word.syllables) - 1)
                word.syllables[handoff].stressed = True
            return

        # --- NEW: splice in all resulting syllables (handles 1 or many)
        word.syllables = (
            word.syllables[:self.syll_index]
            + subword.syllables
            + word.syllables[self.syll_index + 1:]
        )

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
        self.cluster_policies: list[ClusterPolicyRule] = []


    def apply_rule(self, rule: Rule):
        print(f"\n[DEBUG] Applying rule: {rule.name} ({rule.type})")

        # make cluster policies visible to any PhonoRule subclass
        if isinstance(rule, PhonoRule):
            rule.cluster_policies = self.cluster_policies

        for word in self.words:
            before = word.to_string()
            rule.apply(word)
            after = word.to_string()

            if self.log_steps and before != after:
                word.log_step(rule.name, before, after)
            
            print(f"[DEBUG]   Result for '{before}' -> '{after}'")


    def evolve(self, rule_data_list: list):
        self.cluster_policies.clear()
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
        elif rule_type == "clp":
            rule = ClusterPolicyRule(expanded_data)
            self.cluster_policies.append(rule)
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
