# core/test_tokenizer_latin.py

from core.latin import PhonoLatin
from evolution.tokenizer import Tokenizer, DEFAULT_IPA_UNITS


def make_strict_latin_tokenizer():
    legal_compounds = {
        "ae", "au", "oe", "ei", "ui",
        "kʷ", "gʷ",
        "r̩", "l̩", "m̩", "n̩",
    }
    return Tokenizer(
        units=DEFAULT_IPA_UNITS,
        legal_units=None,
        legal_compounds=legal_compounds,
        strict_compounds=True
    )


def make_permissive_tokenizer():
    return Tokenizer(units=DEFAULT_IPA_UNITS, strict_compounds=False)


def test_known_sentence_against_expected():
    expected_words = [
        "ˈan",
        "ˈnɛs.kiːs",
        "ˈmiː",
        "ˈfiː.liː",
        "kʷan.ˈtɪl.laː",
        "pruː.ˈdɛn.ti.aː",
        "ˈmʊn.dʊs",
        "rɛ.ˈgaː.tʊr",
    ]
    input_words = ["An", "nescīs,", "mī", "fīlī,", "quantillā", "prūdentiā", "mundus", "regātur?"]
    clean = [w.strip(",?;:!.'\"").lower() for w in input_words]

    lat = PhonoLatin()
    if not hasattr(lat, "tokenizer") or lat.tokenizer is None:
        lat.tokenizer = make_strict_latin_tokenizer()

    outputs = [lat.to_ipa(w, use_override=True, verbose=False) for w in clean]

    assert outputs == expected_words, (
        "Mismatch in known sentence.\n"
        f"Expected:\n  {expected_words}\nGot:\n  {outputs}"
    )


def test_strict_compound_gating():
    tok = make_strict_latin_tokenizer()

    assert tok.tokenize("ae") == ["ae"]
    assert tok.tokenize("ai") == ["a", "i"]
    assert tok.tokenize("kʷa")[:1] == ["kʷ"]

    out = tok.tokenize("tɕa")
    # In strict mode, only whitelisted compounds should be atomic.
    assert out[0] in {"t", "tɕ"}
    if out[0] == "tɕ":
        raise AssertionError("tɕ unexpectedly treated as atomic in strict mode (not whitelisted).")


def test_permissive_mode_allows_emergent_compounds():
    tok = make_permissive_tokenizer()
    toks = tok.tokenize("ai")
    assert toks in (["ai"], ["a", "i"]), f"Unexpected tokenization for 'ai': {toks}"

    tok.add_units(["ai"])
    assert tok.tokenize("ai") == ["ai"]
    assert tok.tokenize("miː") == ["m", "iː"]


if __name__ == "__main__":
    try:
        test_known_sentence_against_expected()
        print("✓ PhonoLatin known sentence: PASS")
        test_strict_compound_gating()
        print("✓ Strict compound gating: PASS")
        test_permissive_mode_allows_emergent_compounds()
        print("✓ Permissive/emergent compounds: PASS")
    except AssertionError as e:
        print("✗ Test failed:\n", e)
        raise
