import json

class Phonologizer:
    def __init__(self, language = "Generic"):
        self.language = language
        self.ipa_map = {}
        self.contextual_rules = []
        self.stress_rules = []

    def tokenize(self, phrase):
        # Split phrase into a list of words
        return phrase.strip().split()
    
    def syllabify(self, word):
        # Stub for syllabification - override in subclass.
        return [word]
    
    def assign_stress(self, syllables):
        # Stub for stress rules - override in subclass. 
        return syllables
    
    def apply_context_rules(self, phonemes):
        # Apply contextual changes (c -> s before e)
        return phonemes
    
    def to_ipa(self,word): 
        # Convert to IPA using mapping and rules
        phonemes = [self.ipa_map.get(char, char) for char in word]
        phonemes = self.apply_context_rules(phonemes)
        return "".join(phonemes)
    
    def convert_phrase(self, phrase):
        words = self.tokenize(phrase)
        return " ".join(self.to_ipa(word) for word in words)
    




