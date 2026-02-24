import importlib.util
import json
import os
import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from PyQt5 import uic


from evolution.evolver import EvolutionEngine
from evolution.orthographer import Orthographer
from interface.preset_edit import UI_Main as Preset_Main
from interface.orthographer_editor import OrthographyEditor

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "presets", "presets.db")
ORTHO_DB_PATH = os.path.join(BASE_DIR, "presets", "orthographies.db")
OVERRIDE_PATH = os.path.join(BASE_DIR, "data", "latin_stress_overrides.json")



class MainApp(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)  # Loads the .ui file

        # === WIDGET CONNECTIONS ===
        self.input_box = self.findChild(QTextEdit, "textEdit_input")
        self.output_box = self.findChild(QTextEdit, "textEdit_output")   
        self.ortho_box = self.findChild(QTextEdit, "textEdit_ortho")    
        self.convert_button = self.findChild(QPushButton, "pushButton_translate")
        self.create_pre_button = self.findChild(QPushButton, "pushButton_create_preset")
        self.create_ortho_button = self.findChild(QPushButton, "pushButton_create_ortho")
        self.base_combo = self.findChild(QComboBox, "comboBox_baseLang")
        self.preset_combo = self.findChild(QComboBox, "comboBox_preset")
        self.ortho_combo = self.findChild(QComboBox, "comboBox_ortho")
        self.from_ipa_button = self.findChild(QPushButton, "pushButton_fromIPA")
        if self.from_ipa_button is not None:
            self.from_ipa_button.clicked.connect(self.translate_from_ipa)

        self.phono = None


        # === EVENT HANDLERS ===
        
        self.populate_base_combo()
        self.populate_preset_combo()
        self.populate_ortho_combo()
        self.convert_button.clicked.connect(self.translate)

        self.preset_editor_window = None
        self.create_pre_button.clicked.connect(self.launch_preset_editor)
        self.create_ortho_button.clicked.connect(self.launch_ortho_editor)
        self.base_combo.currentIndexChanged.connect(self.load_base_language)

        self.show()

    # === BASE LANG METHODS ===
    def load_base_language(self):
        lang_name = self.base_combo.currentText().lower()
        if lang_name == "<select base language>":
            self.phono = None
            return

        module_name = f"core.{lang_name}"
        class_name = f"Phono{lang_name.capitalize()}"

        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            self.phono = cls(override_path=OVERRIDE_PATH)
            print(f"[Loaded] {class_name} from {module_name}")
        except Exception as e:
            print(f"[Error] Could not load {class_name}: {e}")
            self.phono = None



    def populate_base_combo(self, _=None):
        core_dir = os.path.join(BASE_DIR, "core")
        skip_files = {"phonologizer.py", "__init__.py"}

        self.base_combo.clear()
        self.base_combo.addItem("<Select base language>")

        for filename in os.listdir(core_dir):
            if filename.endswith(".py") and filename not in skip_files:
                name = filename.replace(".py", "")
                self.base_combo.addItem(name.capitalize())

    
    # === PRESET METHODS ===
    def launch_preset_editor(self):
        # Reuse an existing editor window if visible
        if self.preset_editor_window and self.preset_editor_window.isVisible():
            self.preset_editor_window.activateWindow()
            self.preset_editor_window.raise_()
            return

        # Pass current preset as the default to open
        current = self.preset_combo.currentText()
        start = current if current and current != "<Select a preset>" else None

        self.preset_editor_window = Preset_Main(start_preset=start)
        self.preset_editor_window.presetSaved.connect(self.on_preset_saved)
        self.preset_editor_window.show()

    def populate_preset_combo(self):
        self.preset_combo.clear()
        self.preset_combo.addItem("<Select a preset>")
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
                tables = [row[0] for row in cursor.fetchall()]
                self.preset_combo.addItems(tables)
        except sqlite3.Error as e:
            print(f"[DB Error] {e}")

    def on_preset_saved(self, name):
        # repopulate the dropdown and reselect the saved preset
        self.populate_preset_combo()
        idx = self.preset_combo.findText(name)
        if idx != -1:
            self.preset_combo.setCurrentIndex(idx)

    def load_selected_rules(self):
        preset_name = self.preset_combo.currentText()
        if not preset_name or preset_name == "<Select a preset>":
            return []

        rules = []
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT rule FROM {preset_name}")
                rows = cursor.fetchall()
                for row in rows:
                    try:
                        rule = json.loads(row[0])
                        if isinstance(rule, list):
                            rules.append(rule)
                    except json.JSONDecodeError as e:
                        print(f"[Error] Could not decode rule: {e}")
        except sqlite3.Error as e:
            print(f"[DB Error] Failed to load rules: {e}")

        return rules
    
    # === ORTHOGRAPHY METHODS ===
    def populate_ortho_combo(self):
        """Fill comboBox_ortho from the DB table 'orth_presets' (name TEXT, data TEXT JSON)."""
        self.ortho_combo.clear()
        self.ortho_combo.addItem("<Select orthography>")
        try:
            with sqlite3.connect(ORTHO_DB_PATH) as conn:
                cur = conn.cursor()
                # If the table doesn't exist, this throws and we fall back gracefully.
                cur.execute("SELECT name FROM orth_presets ORDER BY name COLLATE NOCASE")
                names = [r[0] for r in cur.fetchall()]
                if names:
                    self.ortho_combo.addItems(names)
        except sqlite3.Error as e:
            print(f"[DB Ortho] {e} (no orthography presets table?)")

    def get_selected_orthography_preset(self):
        """
        Returns a dict like:
          {
            "options": {"strip_stress": true, "strip_dots": true, "fuse_nasal": true, "ignore_length": false},
            "map": [["tʃ","ch"], ["ʃ","sc"], ["ã","an"], ["a","a"], ...]
          }
        or None if nothing selected or not found.
        """
        sel = self.ortho_combo.currentText()
        if not sel or sel == "<Select orthography>":
            return None

        try:
            with sqlite3.connect(ORTHO_DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("SELECT data FROM orth_presets WHERE name = ?", (sel,))
                row = cur.fetchone()
                if not row:
                    print(f"[DB Ortho] No data for orthography preset '{sel}'.")
                    return None
                data = json.loads(row[0])
                if not isinstance(data, dict) or "map" not in data:
                    print(f"[DB Ortho] Malformed data for '{sel}'. Expected dict with 'map'.")
                    return None
                return data
        except sqlite3.Error as e:
            print(f"[DB Ortho] Failed to load orthography preset '{sel}': {e}")
        except json.JSONDecodeError as je:
            print(f"[DB Ortho] JSON error for preset '{sel}': {je}")
        return None

    def apply_orthography(self, words):
        """
        words: list[Word] from the engine (supports .to_string()).
        Produces a single orthographic string or a warning text.
        """
        preset = self.get_selected_orthography_preset()
        if not preset:
            return "[Info] No orthography preset selected."

        # Defensive import in case Orthographer is missing during iteration.
        try:
            # Expecting {"options": {...}, "map": [[ipa, orth], ...]}
            options = preset.get("options", {}) or {}
            mapping = preset.get("map", []) or []
            if not mapping:
                return "[Warning] Orthography preset has an empty 'map'."

            og = Orthographer(mapping)

            # Convert engine words: we pass the IPA strings to the orthographer
            ipa_strings = [w.to_string() for w in words]
            ortho_words = [og.transcribe(s) for s in ipa_strings]
            return " ".join(ortho_words)

        except Exception as e:
            print(f"[Ortho] Failed to apply orthography: {e}")
            return f"[Error] Failed to apply orthography: {e}"

    def launch_ortho_editor(self):
        """Launch the orthography editor dialog."""
        current = self.ortho_combo.currentText()
        start = current if current and current != "<Select orthography>" else None

        dlg = OrthographyEditor(self, start_preset=start)
        dlg.exec_()
        self.populate_ortho_combo()

    def translate_from_ipa(self):
        """
        Take whatever IPA is in textEdit_output and run it through
        the currently selected orthography preset. Does NOT touch
        the phonology/rule engine.
        """
        ipa_text = self.output_box.toPlainText().strip()

        if not ipa_text:
            self.ortho_box.setPlainText("[Warning] No IPA output to convert.")
            return

        # Reuse your existing preset loader
        preset = self.get_selected_orthography_preset()
        if not preset:
            self.ortho_box.setPlainText("[Info] No orthography preset selected.")
            return

        try:
            options = preset.get("options", {}) or {}
            mapping = preset.get("map", []) or []
            if not mapping:
                self.ortho_box.setPlainText("[Warning] Orthography preset has an empty 'map'.")
                return

            # Use the same constructor shape as in apply_orthography()
            og = Orthographer(mapping)

            # Split the IPA string by spaces – we already have final IPA
            ipa_words = ipa_text.split()
            if not ipa_words:
                self.ortho_box.setPlainText("[Warning] Nothing to process in IPA output.")
                return

            ortho_words = [og.transcribe(w) for w in ipa_words]
            self.ortho_box.setPlainText(" ".join(ortho_words))

        except Exception as e:
            self.ortho_box.setPlainText(f"[Error] Failed to convert from IPA: {e}")
            print(f"[Debug] Exception in translate_from_ipa(): {e}")


    # === INPUT BOX ===
    def translate(self):
        raw_text = self.input_box.toPlainText().strip()

        if not raw_text:
            self.output_box.setPlainText("[Warning] No input provided.")
            return

        if not self.phono:
            self.output_box.setPlainText("[Warning] No base language selected.")
            return

        rule_data = self.load_selected_rules()
        if not rule_data:
            self.output_box.setPlainText("[Warning] No preset selected or preset is empty.")
            return

        try:
            # 1) Normalize hyphens/dashes to spaces (semi‑vowel safeguard)
            #    Covers: hyphen-minus -, non-breaking hyphen ‑, en dash – , em dash —
            normalized = (
                raw_text
                .replace("\u2011", " ")  # non‑breaking hyphen
                .replace("\u2013", " ")  # en dash
                .replace("\u2014", " ")  # em dash
                .replace("-", " ")       # hyphen-minus
            )

            # 2) Remove common punctuation everywhere (keep IPA chars intact)
            PUNCT = ".,;:!?()[]{}\"'…"  # expand if you run into more
            translator = str.maketrans("", "", PUNCT)
            cleaned = normalized.translate(translator)

            # 3) Lowercase and split
            words = cleaned.lower().split()
            if not words:
                self.output_box.setPlainText("[Warning] Nothing to process after cleaning input.")
                self.ortho_box.setPlainText("")
                return

            # 4) Phonologize
            ipa_words = [self.phono.to_ipa(w) for w in words]
            
            # 5) Evolve
            engine = EvolutionEngine(ipa_words, log_steps=True)
            engine.evolve(rule_data)

            # 6) IPA Output
            ipa_result = " ".join(w.to_string() for w in engine.words)
            self.output_box.setPlainText(ipa_result)

            # Orthography Output
            ortho_result = self.apply_orthography(engine.words)
            self.ortho_box.setPlainText(ortho_result)

        except Exception as e:
            self.output_box.setPlainText(f"[Error] Translation failed: {e}")
            self.ortho_box.setPlainText("")
            print(f"[Debug] Exception in translate(): {e}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    sys.exit(app.exec_())
