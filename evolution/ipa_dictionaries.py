_COMBINING_TILDE = "̃"
_VOWEL_CHARS = set("aeiouyɯɨʉɪʊʏɛɔæœøɐəɞɜʌɑɒ")

def double_nasalize_diph(tok: str) -> str:
    """
    Insert a combining tilde after every vowel letter in the diphthong token.
    Example: 'ai' -> 'ãĩ', 'iə' -> 'ĩə̃', 'ɔi' -> 'ɔ̃ĩ'
    - Idempotent: if a vowel is already nasalized (next char = ̃), it won't add another.
    - Leaves any trailing length marks (ː) untouched.
    """
    out = []
    i = 0
    while i < len(tok):
        ch = tok[i]
        out.append(ch)

        # nasalize each vowel letter (but don't duplicate if already nasalized)
        if ch in _VOWEL_CHARS:
            nxt = tok[i + 1] if i + 1 < len(tok) else ""
            if nxt != _COMBINING_TILDE:
                out.append(_COMBINING_TILDE)
        i += 1
    return "".join(out)



IPA_GROUPS = {
    # ===== CONS by MANNER
    "Nasals": [
        'm̥', 'm', 'ɱ̊', 'ɱ', 'n̼', 'n̥', 'n', 'ɳ̊', 'ɳ', 'ɲ̊', 'ɲ', 'ŋ̊', 'ŋ', 'ɴ̥', 'ɴ'
    ],

    "Plosives": [
        'p', 'b', 'p̪', 'b̪', 't̼', 'd̼', 't̪', 'd̪', 't', 'd', 'ʈ', 'ɖ', 'c', 'ɟ', 'k', 'ɡ', 'q', 'ɢ', 'ʡ', 'ʔ'
    ],

    "SibilantAffricates": [
        't̪s̪', 'd̪z̪', 'ts', 'dz', 't̠ʃ', 'd̠ʒ', 'tʂ', 'dʐ', 'tɕ', 'dʑ'
    ],

    "NonSibilantAffricates": [
        'pɸ', 'bβ', 'p̪f', 'b̪v', 't̪θ', 'd̪ð', 'tɹ̝̊', 'dɹ̝', 't̠ɹ̠̊˔', 'd̠ɹ̠˔', 'cç', 'ɟʝ', 'kx', 'ɡɣ', 'qχ', 'ɢʁ', 'ʡʜ', 'ʡʢ', 'ʔh' 
    ],

    "SibilantFricatives": [
        's', 'z', 'ʃ', 'ʒ', 'ʂ', 'ʐ', 'ɕ', 'ʑ'
    ],

    "NonSibilantFricatives": [
        'ɸ', 'β', 'f', 'v', 'θ̼', 'ð̼', 'θ', 'ð', 'θ̠', 'ð̠', 'ɹ̠̊˔', 'ɹ̠˔', 'ɻ̊˔', 'ɻ˔', 'ç', 'ʝ', 'x', 'ɣ', 'χ', 'ʁ', 'ħ', 'ʕ', 'h', 'ɦ'
    ],

    "Approximants": [
        'β̞', 'ʋ', 'ð̞', 'ɹ', 'ɹ̠', 'ɻ', 'j', 'ɰ', 'ʁ̞'
    ],

    "Taps": [
        'ⱱ̟', 'ⱱ', 'ɾ̼', 'ɾ̥', 'ɾ', 'ɽ̊','ɽ', 'ɢ̆', 'ʡ̆'
    ],

    "Trills": [
        'ʙ̥', 'ʙ', 'r̥', 'r', 'r̠', 'ɽ̊r̥', 'ɽr', 'ʀ̥', 'ʀ', 'ʜ', 'ʢ' 
    ],

    "LateralAffricates": [
        'tɬ', 'dɮ', 'tꞎ', 'd𝼅', 'c𝼆', 'ɟʎ̝', 'k𝼄', 'ɡʟ̝'
    ],

    "LateralFricatives": [
        'ɬ', 'ɮ', 'ꞎ', '𝼅', '𝼆', 'ʎ̝', '𝼄', 'ʟ̝' 
    ],

    "LateralApproximants": [
        'l̪', 'l', 'l̠', 'ɭ', 'ʎ', 'ʟ', 'ʟ̠'
    ],

    "LateralTaps": [
        'ɺ̥','ɺ', '𝼈̊', '𝼈', 'ʎ̆', 'ʟ̆'
    ], 

    # ===== CONS by PLACE =====
    "Bilabials": [
        'm̥', 'm', 'p', 'b', 'pɸ', 'bβ','ɸ', 'β', 'β̞', 'ʙ̥', 'ʙ', 'ⱱ̟',
    ],
    "Labiodentals": [
        'ɱ̊', 'ɱ', 'p̪', 'b̪', 'f', 'v', 'ʋ', 'ⱱ'
    ],
    "Linguolabials": [
        'n̼', 't̼', 'd̼', 'θ̼', 'ð̼', 'ɾ̼', 
    ],
    "Dentals": [
        't̪', 'd̪', 't̪s̪', 'd̪z̪', 't̪θ', 'd̪ð', 'θ', 'ð', 'ð̞', 'l̪'
    ],
    "Alveolars": [
        'n̥', 'n', 't', 'd', 'ts', 'dz', 'tɹ̝̊', 'dɹ̝', 's', 'z', 'θ̠', 'ð̠', 'ɹ', 'ɾ̥', 'ɾ', 'r̥', 'r', 'tɬ', 'dɮ', 'ɬ', 'ɮ', 'l', 'ɺ̥','ɺ',
    ],
    "PostAlveolars": [
        't̠ʃ', 'd̠ʒ', 't̠ɹ̠̊˔', 'd̠ɹ̠˔', 'ʃ', 'ʒ', 'ɹ̠̊˔', 'ɹ̠˔', 'ɹ̠', 'r̠', 'l̠'
    ],
    "Retroflexs": [
        'ɳ̊', 'ɳ', 'ʈ', 'ɖ', 'tʂ', 'dʐ', 'ʂ', 'ʐ', 'ɻ̊˔', 'ɻ˔', 'ɻ', 'ɽ̊', 'ɽ', 'ɽ̊r̥', 'ɽr', 'tꞎ', 'd𝼅', 'ꞎ', '𝼅', '𝼈̊', '𝼈', 'ɭ'
    ],
    "Palatals": [
        'ɲ̊', 'ɲ', 'c', 'ɟ', 'tɕ', 'dʑ', 'cç', 'ɟʝ', 'ɕ', 'ʑ', 'ç', 'ʝ', 'j', 'c𝼆', 'ɟʎ̝', '𝼆', 'ʎ̝', 'ʎ̆'
    ],
    "Velars": [
        'ŋ̊', 'ŋ', 'k', 'ɡ', 'kx', 'ɡɣ', 'x', 'ɣ', 'ɰ', 'k𝼄', 'ɡʟ̝', '𝼄', 'ʟ̝', 'ʟ', 'ʟ̆'
    ],
    "Uvulars": [
        'ɴ̥', 'ɴ', 'q', 'ɢ', 'qχ', 'ɢʁ', 'χ', 'ʁ', 'ʁ̞', 'ɢ̆', 'ʀ̥', 'ʀ', 'ʟ̠'
    ],
    "Epiglottals": [
        'ʡ', 'ʡʜ', 'ʡʢ', 'ħ', 'ʕ', 'ʡ̆', 'ʜ', 'ʢ',
    ],
    "Glottals": [
        'ʔ', 'ʔh', 'h', 'ɦ', 'ʔ̞'
    ],
    # ===== CONS by FLOW =====

    "Obstruents" : [
        'p', 'b', 'p̪', 'b̪', 't̼', 'd̼', 't̪', 'd̪', 't', 'd', 'ʈ', 'ɖ', 'c', 'ɟ', 'k', 'ɡ', 'q', 'ɢ', 'ʡ', 'ʔ',
        't̪s̪', 'd̪z̪', 'ts', 'dz', 't̠ʃ', 'd̠ʒ', 'tʂ', 'dʐ', 'tɕ', 'dʑ', 'pɸ', 'bβ', 'p̪f', 'b̪v', 
        't̪θ', 'd̪ð', 'tɹ̝̊', 'dɹ̝', 't̠ɹ̠̊˔', 'd̠ɹ̠˔', 'cç', 'ɟʝ', 'kx', 'ɡɣ', 'qχ', 'ɢʁ', 'ʡʜ', 'ʡʢ', 'ʔh', 's', 
        'z', 'ʃ', 'ʒ', 'ʂ', 'ʐ', 'ɕ', 'ʑ', 'ɸ', 'β', 'f', 'v', 'θ̼', 'ð̼', 'θ', 'ð', 'θ̠', 'ð̠', 'ɹ̠̊˔', 'ɹ̠˔', 
        'ɻ̊˔', 'ɻ˔', 'ç', 'ʝ', 'x', 'ɣ', 'χ', 'ʁ', 'ħ', 'ʕ', 'h', 'ɦ'
    ],
    "VoicedObstruents" : [
        'b', 'b̪', 'd̼', 'd̪', 'd', 'ɖ', 'ɟ', 'ɡ', 'ɢ', 
        'd̪z̪', 'dz', 'd̠ʒ', 'dʐ', 'dʑ',
        'bβ', 'b̪v', 'd̪ð', 'dɹ̝', 'd̠ɹ̠˔', 'ɟʝ', 'ɡɣ', 'ɢʁ', 'ʡʢ',
        'z', 'ʒ', 'ʐ', 'ʑ', 'β', 'v', 'ð̼', 'ð', 'ð̠', 'ɹ̠˔', 'ɻ˔', 'ʝ', 'ɣ', 'ʁ', 'ʕ', 'ɦ'
    ],
    "VoicelessObstruents" : [
        'p', 'p̪', 't̼', 't̪', 't', 'ʈ', 'c', 'k', 'q', 'ʡ', 'ʔ',
        't̪s̪', 'ts', 't̠ʃ', 'tʂ', 'tɕ',
        'pɸ', 'p̪f', 't̪θ', 'tɹ̝̊', 't̠ɹ̠̊˔', 'cç', 'kx', 'qχ', 'ʡʜ', 'ʔh',
        's', 'ʃ', 'ʂ', 'ɕ', 'ɸ', 'f', 'θ̼', 'θ', 'θ̠', 'ɹ̠̊˔', 'ɻ̊˔', 'ç', 'x', 'χ', 'ħ', 'h'
    ],

    "Sonorants" : [
        'm̥', 'm', 'ɱ̊', 'ɱ', 'n̼', 'n̥', 'n', 'ɳ̊', 'ɳ', 'ɲ̊', 'ɲ', 'ŋ̊', 'ŋ', 'ɴ̥', 'ɴ', 'β̞', 'ʋ', 'ð̞', 'ɹ', 'ɹ̠',
        'ɻ', 'j', 'ɰ', 'ʁ̞', 'ⱱ̟', 'ⱱ', 'ɾ̼', 'ɾ̥', 'ɾ', 'ɽ̊','ɽ', 'ɢ̆', 'ʡ̆', 'ʙ̥', 'ʙ', 'r̥', 'r', 'r̠', 'ɽ̊r̥', 'ɽr',
        'ʀ̥', 'ʀ', 'ʜ', 'ʢ', 'tɬ', 'dɮ', 'tꞎ', 'd𝼅', 'c𝼆', 'ɟʎ̝', 'k𝼄', 'ɡʟ̝', 'ɬ', 'ɮ', 'ꞎ', '𝼅', '𝼆', 'ʎ̝', 
        '𝼄', 'ʟ̝', 'l̪', 'l', 'l̠', 'ɭ', 'ʎ', 'ʟ', 'ʟ̠', 'ɺ̥','ɺ', '𝼈̊', '𝼈', 'ʎ̆', 'ʟ̆'
    ], 
    "VoicedSonorants" : [
        'm', 'ɱ', 'n̼', 'n', 'ɳ', 'ɲ', 'ŋ', 'ɴ',
        'β̞', 'ʋ', 'ð̞', 'ɹ', 'ɹ̠', 'ɻ', 'j', 'ɰ', 'ʁ̞', 'ʔ̞',
        'ⱱ̟', 'ⱱ', 'ɾ̼', 'ɾ', 'ɽ', 'ɢ̆', 'ʡ̆',
        'ʙ', 'r', 'r̠', 'ɽr', 'ʀ', 'ʢ',
        'dɮ', 'd𝼅', 'ɟʎ̝', 'ɡʟ̝',
        'ɮ', '𝼅', 'ʎ̝', 'ʟ̝',
        'l̪', 'l', 'l̠', 'ɭ', 'ʎ', 'ʟ', 'ʟ̠',
        'ɺ', '𝼈', 'ʎ̆', 'ʟ̆'
    ],
    "VoicelessSonorants" : [
        'm̥', 'ɱ̊', 'n̥', 'ɳ̊', 'ɲ̊', 'ŋ̊', 'ɴ̥',
        'ɾ̥', 'ɽ̊',
        'ʙ̥', 'r̥', 'ɽ̊r̥', 'ʀ̥', 'ʜ',
        'tɬ', 'tꞎ', 'c𝼆', 'k𝼄',
        'ɬ', 'ꞎ', '𝼆', '𝼄',
        'ɺ̥', '𝼈̊'
    ],

    # ===== VOWELS by HEIGHT =====
    "CloseVowels": [
        'i', 'y', 'ɨ', 'ʉ', 'ɯ', 'u',
        'iː', 'yː', 'ɨː', 'ʉː', 'ɯː', 'uː',
        'ĩ', 'ỹ', 'ɨ̃', 'ʉ̃', 'ɯ̃', 'ũ',
        'ĩː', 'ỹː', 'ɨ̃ː', 'ʉ̃ː', 'ɯ̃ː', 'ũː',
        'ĩːː', 'ỹːː', 'ɨ̃ːː', 'ʉ̃ːː', 'ɯ̃ːː', 'ũːː'
    ],
    "NearCloseVowels": [
        'ɪ', 'ʏ', 'ʊ',
        'ɪː', 'ʏː', 'ʊː',
        'ɪ̃', 'ʏ̃', 'ʊ̃',
        'ɪ̃ː', 'ʏ̃ː', 'ʊ̃ː',
        'ɪ̃ːː', 'ʏ̃ːː', 'ʊ̃ːː'
    ],
    "CloseMidVowels": [
        'e', 'ø', 'ɘ', 'ɵ', 'ɤ', 'o',
        'eː', 'øː', 'ɘː', 'ɵː', 'ɤː', 'oː',
        'ẽ', 'ø̃', 'ɘ̃', 'ɵ̃', 'ɤ̃', 'õ',
        'ẽː', 'ø̃ː', 'ɘ̃ː', 'ɵ̃ː', 'ɤ̃ː', 'õː',
        'ẽːː', 'ø̃ːː', 'ɘ̃ːː', 'ɵ̃ːː', 'ɤ̃ːː', 'õːː'
    ],
    "MidVowels": [
        'ə', 'əː', 'ə̃', 'ə̃ː', 'ə̃ːː'
    ],

    "OpenMidVowels": [
        'ɛ', 'œ', 'ɜ', 'ɞ', 'ʌ', 'ɔ',
        'ɛː', 'œː', 'ɜː', 'ɞː', 'ʌː', 'ɔː',
        'ɛ̃', 'œ̃', 'ɜ̃', 'ɞ̃', 'ʌ̃', 'ɔ̃',
        'ɛ̃ː', 'œ̃ː', 'ɜ̃ː', 'ɞ̃ː', 'ʌ̃ː', 'ɔ̃ː',
        'ɛ̃ːː', 'œ̃ːː', 'ɜ̃ːː', 'ɞ̃ːː', 'ʌ̃ːː', 'ɔ̃ːː'
    ],
    "NearOpenVowels": [
        'æ', 'ɐ',
        'æː', 'ɐː',
        'æ̃', 'ɐ̃',
        'æ̃ː', 'ɐ̃ː',
        'æ̃ːː', 'ɐ̃ːː'
    ],
    "OpenVowels": [
        'a', 'ɶ', 'ä', 'ɑ', 'ɒ',
        'aː', 'ɶː', 'äː', 'ɑː', 'ɒː',
        'ã', 'ɶ̃', 'ä̃', 'ɑ̃', 'ɒ̃',
        'ãː', 'ɶ̃ː', 'ä̃ː', 'ɑ̃ː', 'ɒ̃ː',
        'ãːː', 'ɶ̃ːː', 'ä̃ːː', 'ɑ̃ːː', 'ɒ̃ːː'
    ],

    # ===== VOWELS by POSITION
    "FrontVowels": [
        'i', 'y', 'ɪ', 'ʏ', 'e', 'ø', 'ɛ', 'œ', 'æ', 'a', 'ɶ',
        'iː', 'yː', 'ɪː', 'ʏː', 'eː', 'øː', 'ɛː', 'œː', 'æː', 'aː', 'ɶː',
        'ĩ', 'ỹ', 'ɪ̃', 'ʏ̃', 'ẽ', 'ø̃', 'ɛ̃', 'œ̃', 'æ̃', 'ã', 'ɶ̃',
        'ĩː', 'ỹː', 'ɪ̃ː', 'ʏ̃ː', 'ẽː', 'ø̃ː', 'ɛ̃ː', 'œ̃ː', 'æ̃ː', 'ãː', 'ɶ̃ː',
        'ĩːː', 'ỹːː', 'ɪ̃ːː', 'ʏ̃ːː', 'ẽːː', 'ø̃ːː', 'ɛ̃ːː', 'œ̃ːː', 'æ̃ːː', 'ãːː', 'ɶ̃ːː'
    ],
    "CentralVowels": [
        'ɨ', 'ʉ', 'ɘ', 'ɵ', 'ə', 'ɜ', 'ɞ', 'ʌ', 'ɐ', 'ä',
        'ɨː', 'ʉː', 'ɘː', 'ɵː', 'əː', 'ɜː', 'ɞː', 'ʌː', 'ɐː', 'äː',
        'ɨ̃', 'ʉ̃', 'ɘ̃', 'ɵ̃', 'ə̃', 'ɜ̃', 'ɞ̃', 'ʌ̃', 'ɐ̃', 'ä̃',
        'ɨ̃ː', 'ʉ̃ː', 'ɘ̃ː', 'ɵ̃ː', 'ə̃ː', 'ɜ̃ː', 'ɞ̃ː', 'ʌ̃ː', 'ɐ̃ː', 'ä̃ː',
        'ɨ̃ːː', 'ʉ̃ːː', 'ɘ̃ːː', 'ɵ̃ːː', 'ə̃ːː', 'ɜ̃ːː', 'ɞ̃ːː', 'ʌ̃ːː', 'ɐ̃ːː', 'ä̃ːː'
    ],
    "BackVowels": [
        'ɯ', 'u', 'ʊ', 'ɤ', 'o', 'ɔ', 'ɑ', 'ɒ',
        'ɯː', 'uː', 'ʊː', 'ɤː', 'oː', 'ɔː', 'ɑː', 'ɒː',
        'ɯ̃', 'ũ', 'ʊ̃', 'ɤ̃', 'õ', 'ɔ̃', 'ɑ̃', 'ɒ̃',
        'ɯ̃ː', 'ũː', 'ʊ̃ː', 'ɤ̃ː', 'õː', 'ɔ̃ː', 'ɑ̃ː', 'ɒ̃ː',
        'ɯ̃ːː', 'ũːː', 'ʊ̃ːː', 'ɤ̃ːː', 'õːː', 'ɔ̃ːː', 'ɑ̃ːː', 'ɒ̃ːː'
    ],
    # ===== VOWELS by ROUNDNESS =====
    "RoundedVowels" : [
    'u', 'ʊ', 'o', 'ɔ', 'y', 'ʏ', 'ø', 'œ', 'ɞ', 'ɵ', 'ɶ',
    'uː', 'ʊː', 'oː', 'ɔː', 'yː', 'ʏː', 'øː', 'œː', 'ɞː', 'ɵː', 'ɶː',
    'ũ', 'ʊ̃', 'õ', 'ɔ̃', 'ỹ', 'ʏ̃', 'ø̃', 'œ̃', 'ɞ̃', 'ɵ̃', 'ɶ̃',
    'ũː', 'ʊ̃ː', 'õː', 'ɔ̃ː', 'ỹː', 'ʏ̃ː', 'ø̃ː', 'œ̃ː', 'ɞ̃ː', 'ɵ̃ː', 'ɶ̃ː',
    'ũːː', 'ʊ̃ːː', 'õːː', 'ɔ̃ːː', 'ỹːː', 'ʏ̃ːː', 'ø̃ːː', 'œ̃ːː', 'ɞ̃ːː', 'ɵ̃ːː', 'ɶ̃ːː'
    ],

    "UnroundedVowels" : [
    'i', 'ɪ', 'e', 'ɛ', 'æ', 'a', 'ɨ', 'ɐ', 'ə', 'ʌ', 'ɑ',
    'iː', 'ɪː', 'eː', 'ɛː', 'æː', 'aː', 'ɨː', 'ɐː', 'əː', 'ʌː', 'ɑː',
    'ĩ', 'ɪ̃', 'ẽ', 'ɛ̃', 'æ̃', 'ã', 'ɨ̃', 'ɐ̃', 'ə̃', 'ʌ̃', 'ɑ̃',
    'ĩː', 'ɪ̃ː', 'ẽː', 'ɛ̃ː', 'æ̃ː', 'ãː', 'ɨ̃ː', 'ɐ̃ː', 'ə̃ː', 'ʌ̃ː', 'ɑ̃ː',
    'ĩːː', 'ɪ̃ːː', 'ẽːː', 'ɛ̃ːː', 'æ̃ːː', 'ãːː', 'ɨ̃ːː', 'ɐ̃ːː', 'ə̃ːː', 'ʌ̃ːː', 'ɑ̃ːː'
    ],
    # ===== VOWELS by LENGTH =====
    "ShortVowels" : [
    "i", "y", "ɪ", "ʏ", "e", "ø", "ɛ", "œ", "æ", "a", "ɶ", "ɨ", "ʉ",
    "ɘ", "ɵ", "ə", "ɜ", "ɞ", "ʌ", "ɐ", "ä", "ɯ", "u", "ʊ", "ɤ", "o", "ɔ", "ɑ", "ɒ"
    ],

    "LongVowels" : [],
    "OverlongVowels" : [],

    # ===== DIPHTHONGS =====
    "Diphthongs" : [
        # Pan-Indo-European core
        "ai", "au", "ei", "oi", "ou", "ui", "eu", "iu",
        # Fronted sets
        "ie", "ia", "io", "ye", "ya", "yo",
        # Backed clusters (Romance, Germanic, etc.)
        "ua", "ue", "uo",
        # Open/mid combos
        "ae", "ao", "eo", "oe",
        # Extended IE/Greek/Slavic
        "ei", "ai", "oi", "au", "eu",
        # Southeast Asian style
        "iə", "iɛ", "iɑ", "ia",
        "uə", "uɛ", "uo", "ua",
        "ɯa", "ɯə",
        # Misc other common
        "eo", "oa", "oe", "ao", "ɛi", "ɔi", "æi",
        "ɑi", "ɑu", "ɔu", "ɛu",
    ],

    "NasalDiphthongs" : [], 
    
    # ===== MISCELANEOUS =====
    "Glides": ['j', 'w', 'ɥ', 'ɰ'],
    "SyllabicConsonants" : ['r̩','l̩','m̩','n̩'],
    "LabioVelars" : ['kʷ', 'ɡʷ', 'xʷ', 'ɣʷ', 'ŋʷ'],

    "Consonants" : [],
    "Fricatives" : [],
    
    "NasalVowels" : [],
    "NasalShortVowels" : [],
    "NasalLongVowels" : [],
    "NasalOverlongVowels" : [],

    "Nuclei" : [],
    "Vocoids" : [],

    "Boundary" : ['.']
}

# CONSONANTS
if not IPA_GROUPS["Consonants"]:
    parts = (
        IPA_GROUPS["Nasals"]
        + IPA_GROUPS["Plosives"]
        + IPA_GROUPS["SibilantAffricates"]
        + IPA_GROUPS["NonSibilantAffricates"]
        + IPA_GROUPS["SibilantFricatives"]
        + IPA_GROUPS["NonSibilantFricatives"]
        + IPA_GROUPS["Approximants"]
        + IPA_GROUPS["Taps"]
        + IPA_GROUPS["Trills"]
        + IPA_GROUPS["LateralAffricates"]
        + IPA_GROUPS["LateralFricatives"]
        + IPA_GROUPS["LateralApproximants"]
        + IPA_GROUPS["LateralTaps"]
    )
    IPA_GROUPS["Consonants"] = list(dict.fromkeys(parts))

if not IPA_GROUPS["Fricatives"]:
    IPA_GROUPS["Fricatives"] = (
        IPA_GROUPS["NonSibilantFricatives"]
        + IPA_GROUPS["SibilantFricatives"]
    )

# Longs
if not IPA_GROUPS["LongVowels"]:
    IPA_GROUPS["LongVowels"] = [v + "ː" for v in IPA_GROUPS["ShortVowels"]]

if not IPA_GROUPS["OverlongVowels"]:
    IPA_GROUPS["OverlongVowels"] = [v + "ːː" for v in IPA_GROUPS["ShortVowels"]]

# Nasalizations
if not IPA_GROUPS["NasalShortVowels"]:
    IPA_GROUPS["NasalShortVowels"] = [v + "̃" for v in IPA_GROUPS["ShortVowels"]]

if not IPA_GROUPS["NasalLongVowels"]:
    IPA_GROUPS["NasalLongVowels"] = [v[:-1] + "̃ː" for v in IPA_GROUPS["LongVowels"]]  # replace trailing ː with ̃ː

if not IPA_GROUPS["NasalOverlongVowels"]:
    IPA_GROUPS["NasalOverlongVowels"] = [v[:-2] + "̃ːː" for v in IPA_GROUPS["OverlongVowels"]]  # ːː -> ̃ːː

if not IPA_GROUPS["NasalVowels"]:
    IPA_GROUPS["NasalShortVowels"] = (
        IPA_GROUPS["NasalLongVowels"]
        + IPA_GROUPS["NasalOverlongVowels"]
    )

IPA_GROUPS["Diphthongs"] = list(dict.fromkeys(IPA_GROUPS["Diphthongs"]))  # dedupe

# Build nasal diphthongs (double tilde), but DO NOT merge back into Diphthongs
if IPA_GROUPS.get("Diphthongs") and not IPA_GROUPS.get("NasalDiphthongs"):
    IPA_GROUPS["NasalDiphthongs"] = [double_nasalize_diph(d) for d in IPA_GROUPS["Diphthongs"]]

if not IPA_GROUPS["Nuclei"]:
    IPA_GROUPS["Nuclei"] = list(dict.fromkeys(
        IPA_GROUPS["CloseVowels"]
        + IPA_GROUPS["NearCloseVowels"]
        + IPA_GROUPS["CloseMidVowels"]
        + IPA_GROUPS["MidVowels"]
        + IPA_GROUPS["OpenMidVowels"]
        + IPA_GROUPS["NearOpenVowels"]
        + IPA_GROUPS["OpenVowels"]
        + IPA_GROUPS["Diphthongs"]
        + IPA_GROUPS["NasalDiphthongs"]
        + IPA_GROUPS["SyllabicConsonants"]
    ))

if not IPA_GROUPS["Vocoids"]:
    IPA_GROUPS["Vocoids"] = list(dict.fromkeys(
        IPA_GROUPS["Nuclei"] + IPA_GROUPS.get("Glides", [])
    ))


__all__ = ["IPA_GROUPS", "expand_group_keywords", "validate_ipa_groups", "tokens_for"]

def tokens_for(*group_names: str) -> set[str]:
    out: set[str] = set()
    for g in group_names:
        out.update(IPA_GROUPS.get(g, []))
    return out

def validate_ipa_groups(strict: bool = False) -> None:
    """
    Light sanity checks. Set strict=True to raise on problems; otherwise prints warnings.
    """
    def warn(msg: str):
        if strict:
            raise ValueError(msg)
        else:
            print(f"[IPA GROUPS warning] {msg}")

    # 1) Shapes
    for name, vals in IPA_GROUPS.items():
        if not isinstance(vals, list):
            warn(f"Group '{name}' is {type(vals).__name__}; expected list.")
            continue
        for i, tok in enumerate(vals):
            if not isinstance(tok, str):
                warn(f"Group '{name}' element {i} is {type(tok).__name__}; expected str.")
            if tok == "":
                warn(f"Group '{name}' contains an empty string at index {i}.")

    # 2) Long vs. Overlong distinct
    long_set = set(IPA_GROUPS.get("LongVowels", []))
    over_set = set(IPA_GROUPS.get("OverlongVowels", []))
    if long_set & over_set:
        warn("LongVowels and OverlongVowels overlap; they should be distinct (ː vs ːː).")

    # 3) Duplicates inside groups
    for name, vals in IPA_GROUPS.items():
        seen, dups = set(), set()
        for tok in vals:
            if tok in seen:
                dups.add(tok)
            seen.add(tok)
        if dups:
            warn(f"Group '{name}' has duplicates: {sorted(dups)}")

def expand_group_keywords(data):
    """
    Expands *Group or *GroupA+GroupB keywords into IPA group values or cross-products.
    """
    def expand_token(token):
        if not token.startswith("*"):
            return [token]
        
        if token in ("*Blank", "*NULL"):
            return [token]

        # Split by '+' after removing the '*'
        parts = token[1:].split('+')
        group_lists = []
        for part in parts:
            group = IPA_GROUPS.get(part)
            if group is None:
                print(f"[Warning] Unknown IPA group: '{part}'")
                return [token]  # Return original if unknown
            group_lists.append(group)

        # Compute Cartesian product
        from itertools import product
        return [''.join(p) for p in product(*group_lists)]

    if isinstance(data, list):
        result = []
        for item in data:
            if isinstance(item, str):
                result.extend(expand_token(item))
            elif isinstance(item, list):
                result.append(expand_group_keywords(item))
            else:
                result.append(item)
        return result
    return data

# Run a non-strict check at import (flip to strict=True if you prefer hard failures)
validate_ipa_groups(strict=False)