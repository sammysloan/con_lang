import json
from core.phonologizer import Phonologizer


class PhonoAkkadian(Phonologizer):
    def __init__(self, override_path = None):
        super().__init__(language = "Akkadian")