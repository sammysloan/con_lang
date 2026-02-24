# orthographer.py
from .tokenizer import Tokenizer, DEFAULT_IPA_UNITS

# orthographer.py
from .tokenizer import Tokenizer, DEFAULT_IPA_UNITS

class Orthographer:
    """
    Very simple orthography mapper:
      - removes stress marks, dots, and length marks automatically
      - fuses nasalized vowels (a + ̃ → ã)
      - greedily replaces IPA sequences using the longest match in mapping
    """

    def __init__(self, mapping):
        # mapping: list of [ipa, orth] pairs
        self.tok = Tokenizer(DEFAULT_IPA_UNITS, strict_compounds=False)
        self.map = {ipa: ortho for ipa, ortho in mapping}
        self.keys_desc = sorted(self.map.keys(), key=len, reverse=True)

    @staticmethod
    def _prep(s: str) -> str:
        # Strip stress, syllable dots, and length markers.
        return s.replace("ˈ", "").replace("ˌ", "").replace(".", "").replace("ː", "")

    def _fuse_nasal(self, toks):
        out, i = [], 0
        while i < len(toks):
            if i + 1 < len(toks) and toks[i + 1] == "̃":
                out.append(toks[i] + "̃")
                i += 2
            else:
                out.append(toks[i])
                i += 1
        return out

    def transcribe(self, ipa_word: str) -> str:
        """Convert IPA to orthographic form using the preset mapping."""
        s = self._prep(ipa_word)
        toks = self.tok.tokenize(s)
        toks = self._fuse_nasal(toks)
        text = "".join(toks)

        out = []
        i, n = 0, len(text)
        while i < n:
            for k in self.keys_desc:
                if text.startswith(k, i):
                    out.append(self.map[k])
                    i += len(k)
                    break
            else:
                # no mapping found, copy raw symbol
                out.append(text[i])
                i += 1
        return "".join(out)

