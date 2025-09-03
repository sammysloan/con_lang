import importlib.util
import json
import os
import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from PyQt5 import uic


from evolution.evolver import EvolutionEngine
from interface.preset_edit import UI_Main as Preset_Main

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "presets", "presets.db")
OVERRIDE_PATH = os.path.join(BASE_DIR, "data", "latin_stress_overrides.json")



class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)  # Loads the .ui file

        # === WIDGET CONNECTIONS ===
        self.input_box = self.findChild(QTextEdit, "textEdit_input")
        self.output_box = self.findChild(QTextEdit, "textEdit_output")      
        self.convert_button = self.findChild(QPushButton, "pushButton_translate")
        self.create_pre_button = self.findChild(QPushButton, "pushButton_create_preset")
        self.base_combo = self.findChild(QComboBox, "comboBox_baseLang")
        self.preset_combo = self.findChild(QComboBox, "comboBox_preset")
        self.phono = None
        # === EVENT HANDLERS ===
        
        self.populate_base_combo()
        self.populate_preset_combo()
        self.convert_button.clicked.connect(self.translate)

        self.preset_editor_window = None
        self.create_pre_button.clicked.connect(self.launch_preset_editor)
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
    def handle_editor_close(self, event):
        self.setEnabled(True)
        event.accept()

    def launch_preset_editor(self):
        self.setEnabled(False)  # Disable the main app window
        self.preset_editor_window = Preset_Main() # Open preset_edit

        # Re-enable main window after the editor closes
        self.preset_editor_window.closeEvent = self.handle_editor_close


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
                return

            # 4) Phonologize
            ipa_words = [self.phono.to_ipa(w) for w in words]
            
            # 5) Evolve
            engine = EvolutionEngine(ipa_words)
            engine.evolve(rule_data)

            # 6) Output
            result = " ".join(w.to_string() for w in engine.words)
            self.output_box.setPlainText(result)

        except Exception as e:
            self.output_box.setPlainText(f"[Error] Translation failed: {e}")
            print(f"[Debug] Exception in translate(): {e}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    sys.exit(app.exec_())
