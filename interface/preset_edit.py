from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QComboBox, 
                             QDialog, QInputDialog, QLabel, QLineEdit, QListWidget,
                             QListWidgetItem, QMessageBox, QPushButton, 
                             QSpinBox, QRadioButton, QVBoxLayout, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import uic
import json
import os
import sqlite3
import sys



# Set absolute path to 'presets.bd' file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "presets", "presets.db")
UI_PATH = lambda name: os.path.join(BASE_DIR, "interface", name)

"""
A note on database structure:
All 'presets' are contained within one database called 'presets.db'
Each 'preset' is contained within its own table
Each 'preset'/table contains a single column, which represents a 'rule'.
Rules are of the SQL TEXT type (Py str)
Rules are later converted to lists using python .split method.
"""

class RuleManager():
    def __init__(self):
        self._rules_list = []
        self._rules_dict = {}
            
    def clear(self):
        self._rules_list.clear()
        self._rules_dict.clear()

    def add(self, rule):
        key = rule[0]
        self._rules_list.append(rule)
        self._rules_dict[key] = rule

    def remove(self, key):
        rule = self._rules_dict.pop(key, None)
        if rule:
            self._rules_list = [r for r in self._rules_list if r[0] != key]

    def get(self, key):
        return self._rules_dict.get(key)

    def get_all(self):
        return self._rules_list.copy()

    def reorder(self, ordered_keys):
        self._rules_list = [self._rules_dict[k] for k in ordered_keys if k in self._rules_dict]

    def has_key(self, key):
        return key in self._rules_dict

    def __len__(self):
        return len(self._rules_list)

class UI_Main(QMainWindow):
    def __init__(self):
        super(UI_Main, self).__init__()
        uic.loadUi(UI_PATH("evo.ui"), self)

        # Define out widgets
        self.button_save = self.findChild(QPushButton, "pushButton_save")
        self.button_save_as = self.findChild(QPushButton, "pushButton_save_as")
        self.button_manage = self.findChild(QPushButton, "pushButton_manage")
        self.combo_select = self.findChild(QComboBox, "comboBox_preset")
        self.button_phono = self.findChild(QPushButton, "pushButton_phono")
        self.button_lexi = self.findChild(QPushButton, "pushButton_lexi" )
        self.button_gram = self.findChild(QPushButton, "pushButton_gram")
        self.button_edit = self.findChild(QPushButton, "pushButton_edit")
        self.button_delete = self.findChild(QPushButton, "pushButton_delete")
        self.button_clear = self.findChild(QPushButton, "pushButton_clear")
        self.list_widget = self.findChild(QListWidget, "listWidget")

        # Global attrs
        self.is_dirty = False
        self.preset_name = ""
        self.rules = RuleManager()


        """ 
	    Rather than defining conn and cursor hear, they are contained within 
        context managers per method. These with statements ensure that db conns
        are safely closed and transactions can be rolled back if errors occur.
	    """

        # Preset widget functions
        self.populate_combo_box()
        self.button_save.clicked.connect(self.savePreset)
        self.button_save_as.clicked.connect(self.saveAs)
        self.button_manage.clicked.connect(self.manage_presets)

        self.combo_select.currentIndexChanged.connect(self.load_preset)

        self.button_phono.clicked.connect(self.addRule)
        self.list_widget.itemDoubleClicked.connect(self.edit_rule) 
        self.list_widget.setDragDropMode(QListWidget.InternalMove)

        self.button_delete.clicked.connect(self.delete_rule)
        
        self.show() # Show the app

    def populate_combo_box(self, restore_to = None):
        self.combo_select.blockSignals(True)
        self.combo_select.clear()

        self.combo_select.addItem("<Select a preset>") # Default placeholder
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""SELECT name FROM sqlite_master
                    WHERE type='table' AND name != 'sqlite_sequence'""")
                presets = [row[0] for row in cursor.fetchall()]
                self.combo_select.addItems(presets)

                # Reselect previous preset, offset by +1 due to placeholder
                if restore_to and restore_to in presets:
                    index = presets.index(restore_to) + 1
                    self.combo_select.setCurrentIndex(index)
                    self.preset_name = restore_to  # Ensure it's preserved
        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Database Error', str(e))
        finally:
            self.combo_select.blockSignals(False)

# Preset methods
    def closeEvent(self, event):
        if self.is_dirty:
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Would you like to save them before exiting?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if response == QMessageBox.Yes:
                self.savePreset()
                event.accept()  # Proceed with closing
            elif response == QMessageBox.No:
                event.accept()  # Proceed with closing
            else:
                event.ignore()  # Cancel closing
        else:
            event.accept()  # No changes — safe to close

    def manage_presets(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Presets")
        dialog.resize(300, 400)

        layout = QVBoxLayout(dialog)

        # List of preset tables
        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(list_widget)

        # Delete button
        delete_button = QPushButton("Delete Selected Preset")
        layout.addWidget(delete_button)

        # Rename button
        rename_button = QPushButton("Rename Selected Preset")
        layout.addWidget(rename_button)

        # Populate list with presets.db presets
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
                tables = cursor.fetchall()
                for name, in tables:
                    item = QListWidgetItem(name)
                    list_widget.addItem(item)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))
            return
        
        # Delete functionality
        def delete_selected_tables():
    
            selected_items = list_widget.selectedItems()
            if not selected_items:
                QMessageBox.warning(dialog, "No Selection", "Please select a preset to delete")
                return
            
            table_names = [item.text() for item in selected_items]
            confirm = QMessageBox.question(
                dialog, "Confirm Deletion",
                f"Are you sure you want to permanently delete '{len(table_names)} preset(s)'?",
                QMessageBox.Yes | QMessageBox.No
            )


            if confirm == QMessageBox.Yes:
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        cursor = conn.cursor()
                        for table_name in table_names: 
                            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                        conn.commit()

                    for item in selected_items:
                        list_widget.takeItem(list_widget.row(item))
                    QMessageBox.information(dialog, "Success", f"Deleted '{len(table_names)}' preset(s) successfully.")
                    
                    self.populate_combo_box()
                except sqlite3.Error as e:
                    QMessageBox.critical(dialog, "Error", str(e))

        def rename_selected_table():
            selected_items = list_widget.selectedItems()
            if len(selected_items) != 1:
                QMessageBox.warning(dialog, "Invalid Selection", "Please select exactly one preset")
                return
            old_name = selected_items[0].text()

            # Prompt for new name
            new_name, ok = QInputDialog.getText(dialog, "Rename Preset", f"Enter new name for '{old_name}':")
            if not ok or not new_name.strip():
                return
            
            new_name = new_name.strip()

            # Check if name already exists
            existing_names = [list_widget.item(i).text() for i in range(list_widget.count())]
            if new_name in existing_names:
                QMessageBox.warning(dialog, "Name Conflict", f"A preset named '{new_name}' already exists.")
                return
            
            # Attempt rename
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
                    conn.commit()

                # Update the item text
                selected_items[0].setText(new_name)
                QMessageBox.information(dialog, "Success", f"Preset '{old_name}' renamed to '{new_name}'.")
                self.populate_combo_box()
            except sqlite3.Error as e:
                QMessageBox.critical(dialog, "Database Error", str(e))

        delete_button.clicked.connect(delete_selected_tables)
        rename_button.clicked.connect(rename_selected_table)

        dialog.exec_()

        self.combo_select.clear()
        self.populate_combo_box()

    def load_preset(self):
        preset = self.combo_select.currentText()
        if not preset or preset == "<Select a preset>":
            self.preset_name = ""
            self.rules.clear()
            self.list_widget.clear()
            self.is_dirty = False
            return  # Return if no preset selected.
        
        if self.is_dirty:
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Would you like to save them before switching presets?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if response == QMessageBox.Yes:
                self.savePreset()
            elif response == QMessageBox.Cancel:
                # Cancel switching presets
                index = self.combo_select.findText(self.preset_name)
                if index != -1:
                    self.combo_select.blockSignals(True)
                    self.combo_select.setCurrentIndex(index)
                    self.combo_select.blockSignals(False)
                return

        # Continue only if dirty check passes
        self.preset_name = preset
        self.rules.clear()
        self.list_widget.clear()

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT rule FROM {preset}")
                rows = cursor.fetchall()

            for row in rows:
                try:
                    rule = json.loads(row[0])
                    if isinstance(rule, list):
                        self.rules.add(rule)

                        label = f"{rule[0]} - {rule[2]}" if len(rule) > 2 else rule[0]
                        item = QListWidgetItem(label)
                        item.setData(Qt.UserRole, rule[0])
                        self.list_widget.addItem(item)
                except json.JSONDecodeError as e:
                    print(f"Could not decode rule: {row[0]} -> {e}")
            self.is_dirty = False

            print("🔍 Loaded rules:")
            for rule in self.rules.get_all():
                print(rule)
            print("─" * 40)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

        print("Loaded preset: ", preset)

    def savePreset(self):
        if not self.preset_name:
            self.saveAs()
            return

        ordered_keys = []

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            key = item.data(Qt.UserRole)
            if key:
                ordered_keys.append(key)

        if not self.rules.get_all():
            QMessageBox.warning(self, "Cancelled", "No rules to save.")
            return

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DROP TABLE IF EXISTS {self.preset_name}")
                cursor.execute(f"""
                    CREATE TABLE {self.preset_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rule TEXT
                    )
                """)

                for key in ordered_keys:
                    if self.rules.has_key(key):
                        full_rule = self.rules.get(key)
                        if full_rule is not None:
                            rule_string = json.dumps(full_rule)
                            cursor.execute(
                                f"INSERT INTO {self.preset_name} (rule) VALUES (?)",
                                (rule_string,)
                            )
                        else:
                            QMessageBox.warning(self, "Missing Rule", f"Key '{key}' not found in rules.")
                    else:
                        QMessageBox.warning(self, "Missing Rule",
                                            f"Key '{key}' not found in rules.")

                conn.commit()
                self.is_dirty = False

            QMessageBox.information(self, "Success", f"Rules saved to table '{self.preset_name}'.")

            self.populate_combo_box(restore_to=self.preset_name)
            self.load_preset()         

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def saveAs(self):
        # Open QInputDialog to define preset name
        dialog_input, ok = QInputDialog.getText(self, "Save As", "Enter preset name:")
        if not ok or not dialog_input.strip():
            QMessageBox.warning(self, "Cancelled", "No valid preset name provided.")
            return

        self.preset_name = dialog_input.strip()
        print(f"preset_name updated: {self.preset_name}")

        self.savePreset()


# Rule methods
    def addRule(self):
        self.dialog_phono = UI_Phono()
        # Checks for ruleReceived signal from phono; calls handle func
        self.dialog_phono.ruleReceived.connect(self.handle_rule_main)
        self.dialog_phono.exec_()

    def edit_rule(self, item):
        selected_key = item.data(Qt.UserRole)

        # Find matching rule by key
        rule = self.rules.get(selected_key)
        if not rule:
            QMessageBox.warning(self, "Error", f"Rule '{selected_key}' not found.")
            return

        rule_type = rule[1]

        if rule_type == "ass":
            self.dialog_assimilate = UI_Assimilate()
            self.dialog_assimilate.ruleSent.connect(self.update_rule)

            self.dialog_assimilate.lineEdit_name.setText(rule[0])
            self.dialog_assimilate.textEdit_notes.setText(rule[2])
            self.dialog_assimilate.lineEdit_target.setText(" ".join(rule[3]))
            self.dialog_assimilate.lineEdit_trigger.setText(" ".join(rule[4]))
            self.dialog_assimilate.lineEdit_replace.setText(" ".join(rule[5]))
            self.dialog_assimilate.checkBox_prog.setChecked(not rule[6])
            self.dialog_assimilate.checkBox_skip.setChecked(rule[7])
            self.dialog_assimilate.exec_()

        elif rule_type == "con":
            self.dialog_context = UI_Context()
            self.dialog_context.ruleSent.connect(self.update_rule)

            self.dialog_context.lineEdit_name.setText(rule[0])
            self.dialog_context.textEdit_notes.setText(rule[2])
            self.dialog_context.lineEdit_old_list.setText(" ".join(rule[3]))
            self.dialog_context.lineEdit_new_list.setText(" ".join(rule[4]))
            self.dialog_context.lineEdit_pre_trig.setText(" ".join(rule[5]))
            self.dialog_context.lineEdit_post_trig.setText(" ".join(rule[6]))
            self.dialog_context.lineEdit_pre_ex.setText(" ".join(rule[7]))
            self.dialog_context.lineEdit_post_ex.setText(" ".join(rule[8]))
            self.dialog_context.checkBox_skip.setChecked(rule[9])
            self.dialog_context.checkBox_solo.setChecked(rule[10])
            self.dialog_context.exec_()

        elif rule_type == "disc":
            self.dialog_assimilate = UI_Assimilate()
            self.dialog_assimilate.ruleSent.connect(self.update_rule)

            self.dialog_assimilate.lineEdit_name.setText(rule[0])
            self.dialog_assimilate.textEdit_notes.setText(rule[2])
            self.dialog_assimilate.lineEdit_target.setText(" ".join(rule[3]))
            self.dialog_assimilate.lineEdit_trigger.setText(" ".join(rule[4]))
            self.dialog_assimilate.lineEdit_replace.setText(" ".join(rule[5]))
            self.dialog_assimilate.checkBox_prog.setChecked(not rule[6])
            self.dialog_assimilate.checkBox_skip.setChecked(rule[7])
            self.dialog_assimilate.checkBox_disc.setChecked(True)
            self.dialog_assimilate.spinBox_max.setValue(rule[8])
            self.dialog_assimilate.spinBox_max.setEnabled(True)
            self.dialog_assimilate.exec_()

        elif rule_type == "epen":
            self.dialog_epen = UI_Epenthetic()
            self.dialog_epen.ruleSent.connect(self.update_rule)

            self.dialog_epen.lineEdit_name.setText(rule[0])
            self.dialog_epen.textEdit_notes.setText(rule[2])
            self.dialog_epen.lineEdit_old.setText(" ".join(rule[3]))
            self.dialog_epen.lineEdit_new.setText(" ".join(rule[4]))
            self.dialog_epen.combo_position.setCurrentText(rule[5].capitalize())
            self.dialog_epen.lineEdit_pre.setText(" ".join(rule[6]))
            self.dialog_epen.lineEdit_post.setText(" ".join(rule[7]))
            self.dialog_epen.exec_()
        
        elif rule_type == "str":
            self.dialog_stress = UI_Stress()
            self.dialog_stress.ruleSent.connect(self.update_rule)

            self.dialog_stress.lineEdit_name.setText(rule[0])
            self.dialog_stress.textEdit_notes.setText(rule[2])
            self.dialog_stress.combo_mode.setCurrentText(rule[3].capitalize())

            if rule[3] == "weight":
                self.dialog_stress.combo_fallback.setCurrentText(rule[4].capitalize())
                self.dialog_stress.spin_window.setValue(rule[5])
                self.dialog_stress.check_coda.setChecked(rule[6])
                self.dialog_stress.check_skip.setChecked(rule[7])

            self.dialog_stress.exec_()

        elif rule_type == "syll":
            self.dialog_syll = UI_Syllabic()
            self.dialog_syll.ruleSent.connect(self.update_rule)

            self.dialog_syll.lineEdit_name.setText(rule[0])
            self.dialog_syll.textEdit_notes.setText(rule[2])
            self.dialog_syll.lineEdit_old_list.setText(" ".join(rule[3]))
            self.dialog_syll.lineEdit_new_list.setText(" ".join(rule[4]))
            self.dialog_syll.comboBox.setCurrentText(str(rule[5]))
            self.dialog_syll.exec_()

        self.is_dirty = True

    def delete_rule(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return

        count = len(selected_items)
        confirm = QMessageBox.question(
            self,
            "Delete Rule(s)?",
            f"Are you sure you want to delete {count} rule{'s' if count > 1 else ''}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        # Collect rows and corresponding rule names
        rows = sorted([self.list_widget.row(item) for item in selected_items], reverse=True)

        for row in rows:
            item = self.list_widget.takeItem(row)
            rule_name = item.text().strip()
            self.rules.remove(rule_name)



    def handle_rule_main(self, rule):
        print("Main received", rule)
        self.rules.add(rule)# Add rule to rules
        print("Updated rules:", self.rules)

        label = f"{rule[0]} - {rule[2]}"  # User-friendly text
        item = QListWidgetItem(label)
        item.setData(Qt.UserRole, rule[0])  # Store actual key
        self.list_widget.addItem(item)

        self.is_dirty = True # Prevent save issues.

    def update_rule(self, updated_rule):
        key = updated_rule[0]
        self.rules.remove(key) # Remove old version
        self.rules.add(updated_rule) # Add new version

        # Updated QListWidget item label
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == key:
                label = f"{updated_rule[0]} - {updated_rule[2]}" if len(updated_rule) > 2 else updated_rule[0]
                item.setText(label)
                break
        self.is_dirty = True


class UI_Dialog(QDialog):
    ruleSent = pyqtSignal(list) # Signal to dialog_phono that rule sent

    def __init__(self):
        super(UI_Dialog, self).__init__()

    def define_widgets(self):
        self.lineEdit_name = self.findChild(QLineEdit, "lineEdit_name") 
        self.textEdit_notes = self.findChild(QTextEdit, "textEdit_notes")
        self.button_close = self.findChild(QPushButton, "pushButton_close")
        self.button_save = self.findChild(QPushButton, "pushButton_save")

        # Clicked methods need UI to ref; thus calls in subclass, not parent

    def child_func(self):
        pass # This will be defined by each subclass instance. 

    def make_rule(self):
        # Setup required inputs
        if self.lineEdit_name.text() and self.textEdit_notes.toPlainText():
            name = self.lineEdit_name.text()
            notes = self.textEdit_notes.toPlainText()
        else: 
            print("No name or notes given. Add to continue.")
            return # This may not be correct keyword to break method. CHECK
        
        self.child_func(name, notes)

    def parse_lineedit(self, text: str):
        """
        Converts space-separated QLineEdit text into a list of phoneme strings,
        replacing '*NULL' with an actual empty string.
        """
        return ["" if val == "*NULL" else val for val in text.split()]

    def send_rule(self, rule):
        print("Func called", rule)
        self.ruleSent.emit(rule)
        self.accept()

class UI_Assimilate(UI_Dialog):
    def __init__(self):
        super(UI_Assimilate, self).__init__()
        uic.loadUi(UI_PATH("dialog_assimilate.ui"), self)

        # Define widgets
        self.define_widgets() # Accept universal dialog widgets
        self.lineEdit_target = self.findChild(QLineEdit, "lineEdit_target")
        self.lineEdit_trigger = self.findChild(QLineEdit, "lineEdit_trigger")
        self.lineEdit_replace = self.findChild(QLineEdit, "lineEdit_replace")
        self.checkBox_disc = self.findChild(QCheckBox, "checkBox_disc")
        self.spinBox_max = self.findChild(QSpinBox, "spinBox_max")
        self.checkBox_prog = self.findChild(QCheckBox, "checkBox_prog")
        self.checkBox_skip = self.findChild(QCheckBox, "checkBox_skip")
        self.label_max = self.findChild(QLabel, "label_max")

        # Add functionality
        self.button_save.clicked.connect(self.make_rule)
        self.button_close.clicked.connect(self.close)

        # Greys out spin box and label unless disc is checked
        self.checkBox_disc.toggled.connect(self.spinBox_max.setEnabled)
        self.checkBox_disc.toggled.connect(self.label_max.setEnabled)
        self.spinBox_max.setEnabled(False)
        self.label_max.setEnabled(False)

    def child_func(self, name, notes):
        if not self.lineEdit_target.text() and not self.lineEdit_trigger.text():
            print("Target or trigger list missing. Add to continue.")
            return

        target_list = self.lineEdit_target.text().split()
        trigger_list = self.lineEdit_trigger.text().split()
        replace_list = self.parse_lineedit(self.lineEdit_replace.text())

        if len(replace_list) != len(target_list):
            QMessageBox.warning(self, "Input Error",
                "Replace list must be the same length as the target list.")
            return

        prog = self.checkBox_prog.isChecked()
        regressive = not prog 
        stress_skip = self.checkBox_skip.isChecked()


        if self.checkBox_disc.isChecked():
            max_distance = self.spinBox_max.value()
            # Create discontiguous assimilation rule
            rule = [name, "disc", notes, target_list, trigger_list, replace_list, 
                    regressive, stress_skip, max_distance]
        else:
            # Create normal assimilation rule
            rule = [name, "ass", notes, target_list, trigger_list, replace_list, 
                    regressive, stress_skip]

        self.send_rule(rule)

class UI_Context(UI_Dialog):
    def __init__(self):
        super(UI_Context, self).__init__()
        uic.loadUi(UI_PATH("dialog_context.ui"), self)

        # Define widgets
        self.define_widgets()
        self.lineEdit_old_list = self.findChild(QLineEdit, "lineEdit_old_list")
        self.lineEdit_new_list = self.findChild(QLineEdit, "lineEdit_new_list")
        self.checkBox_solo = self.findChild(QCheckBox, "checkBox_solo")
        self.checkBox_skip = self.findChild(QCheckBox, "checkBox_skip")
        self.lineEdit_pre_ex = self.findChild(QLineEdit, "lineEdit_pre_ex")
        self.lineEdit_post_ex = self.findChild(QLineEdit, "lineEdit_post_ex")
        self.lineEdit_pre_trig = self.findChild(QLineEdit, "lineEdit_pre_trig")
        self.lineEdit_post_trig = self.findChild(QLineEdit, "lineEdit_post_trig")

        # Add functionality
        self.button_save.clicked.connect(self.make_rule)
        self.button_close.clicked.connect(self.close)

    def child_func(self, name, notes):
        if not self.lineEdit_new_list.text():
            print("No new list given. Add to continue.")
            return
        
        # Setup checkBox functionality
        if self.checkBox_skip.isChecked() == True:
            stress_skip = True
        else: stress_skip = False
        if self.checkBox_solo.isChecked() == True:
            stress_solo = True
        else: stress_solo = False

        # Setup lineEdit functionality
        new_list = self.parse_lineedit(self.lineEdit_new_list.text())
        old_list = self.lineEdit_old_list.text().split()
        pre_ex = self.lineEdit_pre_ex.text().split()
        post_ex = self.lineEdit_post_ex.text().split()
        pre_trig = self.lineEdit_pre_trig.text().split()
        post_trig = self.lineEdit_post_trig.text().split()

        rule = [name, "con", notes, old_list, new_list, pre_trig, post_trig, 
                pre_ex, post_ex, stress_skip, stress_solo]
        
        self.send_rule(rule)

class UI_Epenthetic(UI_Dialog):
    def __init__(self):
        super(UI_Epenthetic, self).__init__()
        uic.loadUi(UI_PATH("dialog_epen.ui"), self)

        # Define widgets
        self.define_widgets()
        self.lineEdit_old = self.findChild(QLineEdit, "lineEdit_old_list")
        self.lineEdit_new = self.findChild(QLineEdit, "lineEdit_new_list")
        self.combo_position = self.findChild(QComboBox, "comboBox")
        self.lineEdit_pre = self.findChild(QLineEdit, "lineEdit_pre_trigs")
        self.lineEdit_post = self.findChild(QLineEdit, "lineEdit_post_trigs")

        self.button_save.clicked.connect(self.make_rule)
        self.button_close.clicked.connect(self.close)

    def child_func(self, name, notes):
        find_list = self.lineEdit_old.text().split()
        new_list = self.parse_lineedit(self.lineEdit_new.text())
        position = self.combo_position.currentText().lower()
        pre_list = self.lineEdit_pre.text().split()
        post_list = self.lineEdit_post.text().split()

        rule = [name, "epen", notes, find_list, new_list, position, pre_list, post_list]
        self.send_rule(rule)

class UI_Stress(UI_Dialog):
    def __init__(self):
        super(UI_Stress, self).__init__()
        uic.loadUi(UI_PATH("dialog_stress.ui"), self)

        # Define universal widgets
        self.define_widgets()

        # Define unique widgets
        self.combo_mode = self.findChild(QComboBox, "comboBox_mode")
        self.combo_fallback = self.findChild(QComboBox, "comboBox_weight_fallback")
        self.spin_window = self.findChild(QSpinBox, "spinBox_window")
        self.check_coda = self.findChild(QCheckBox, "checkBox_coda")
        self.check_skip = self.findChild(QCheckBox, "checkBox_skip")
        self.label_fallback = self.findChild(QLabel, "label_fallback")
        self.label_window = self.findChild(QLabel, "label_window")

        self.button_save.clicked.connect(self.make_rule)
        self.button_close.clicked.connect(self.close)
        self.combo_mode.currentTextChanged.connect(self.toggle_weight_options)
        self.combo_fallback.currentTextChanged.connect(self.toggle_weight_options)


        self.toggle_weight_options()  # Set correct visibility on open

    def toggle_weight_options(self):
        weight_mode = self.combo_mode.currentText().lower() == "weight"
        self.combo_fallback.setEnabled(weight_mode)
        self.spin_window.setEnabled(weight_mode)
        self.check_coda.setEnabled(weight_mode)
        self.check_skip.setEnabled(weight_mode)
        self.label_fallback.setEnabled(weight_mode)
        self.label_window.setEnabled(weight_mode)

        if weight_mode:
            fallback = self.combo_fallback.currentText().strip().lower()
            if fallback == "ultimate":
                self.check_skip.setChecked(False)
                self.check_skip.setEnabled(False)
            else:
                self.check_skip.setEnabled(True)
        else:
            self.check_skip.setChecked(False)
            self.check_skip.setEnabled(False)
        

    def child_func(self, name, notes):
        mode = self.combo_mode.currentText().lower()

        if mode == "weight":
            fallback = self.combo_fallback.currentText().lower()
            window = self.spin_window.value()
            coda = self.check_coda.isChecked()
            skip = self.check_skip.isChecked()
            rule = [name, "str", notes, mode, fallback, window, coda, skip]
        else:
            rule = [name, "str", notes, mode]

        self.send_rule(rule)


class UI_Syllabic(UI_Dialog):
    def __init__(self):
        super(UI_Syllabic, self).__init__()
        uic.loadUi(UI_PATH("dialog_syll.ui"), self)

        # Define widgets
        self.define_widgets() # Accept universal dialog widgets
        self.lineEdit_old_list = self.findChild(QLineEdit, "lineEdit_old_list")
        self.lineEdit_new_list = self.findChild(QLineEdit, "lineEdit_new_list")

        self.lineEdit_pre_trigs = self.findChild(QLineEdit, "lineEdit_pre_trigs")
        self.lineEdit_new_trigs = self.findChild(QLineEdit, "lineEdit_new_trigs")

        self.comboBox = self.findChild(QComboBox, "comboBox")
        self.checkBox_solo = self.findChild(QCheckBox, "checkBox_solo")
        self.checkBox_skip = self.findChild(QCheckBox, "checkBox_skip")
        self.pushButton_save = self.findChild(QPushButton, "pushButton_save")

        # Add functionality
        self.pushButton_save.clicked.connect(self.make_rule)

    def child_func(self, name, notes):
        if not self.lineEdit_new_list.text():
            print("No find values given. Add to continue.")
            return

        # Setup lineEdit functionality
        new_list = self.parse_lineedit(self.lineEdit_new_list.text())
        old_list = self.lineEdit_old_list.text().split()
        position = self.comboBox.currentText().lower()

        rule = [name, "syll", notes, old_list, new_list, position]
        self.send_rule(rule)

class UI_Phono(QDialog):
    # Signal that rule was recieved and sends to main
    ruleReceived = pyqtSignal(list)

    def __init__(self):
        super(UI_Phono, self).__init__()
        uic.loadUi(UI_PATH("dialog_phono.ui"), self)

        # Define widgets
        self.ass = self.findChild(QRadioButton, "radioButton_ass")
        self.con = self.findChild(QRadioButton, "radioButton_con")
        self.epen = self.findChild(QRadioButton, "radioButton_epen")
        self.stress = self.findChild(QRadioButton, "radioButton_stress")
        self.syll = self.findChild(QRadioButton, "radioButton_syll")
        self.button_close = self.findChild(QPushButton, "pushButton_close")
        self.button_create = self.findChild(QPushButton, "pushButton_create")

        # Functionality
        self.button_create.clicked.connect(self.select_type)
        self.button_close.clicked.connect(self.close)

    def select_type(self): 
        print("Select_type called")
        if self.ass.isChecked():
            print("Assimilation selected")
            self.dialog_assimilate = UI_Assimilate()
            self.dialog_assimilate.ruleSent.connect(self.handle_rule_phono)
            self.dialog_assimilate.exec_()

        elif self.con.isChecked():
            print("Contextual selected")
            self.dialog_context = UI_Context()
            self.dialog_context.ruleSent.connect(self.handle_rule_phono)
            self.dialog_context.exec_()
        
        elif self.epen.isChecked():
            print("Epenthetic selected")
            self.dialog_epen = UI_Epenthetic()
            print("Dialog constructed")
            self.dialog_epen.ruleSent.connect(self.handle_rule_phono)
            print("Signal connected")
            self.dialog_epen.exec_()
            print("Dialog executed")

        elif self.stress.isChecked():
            self.dialog_stress = UI_Stress()
            self.dialog_stress.ruleSent.connect(self.handle_rule_phono)
            self.dialog_stress.exec_()

        elif self.syll.isChecked():
            print("Syllabic selected")
            self.dialog_syll = UI_Syllabic()
            self.dialog_syll.ruleSent.connect(self.handle_rule_phono)
            self.dialog_syll.exec_()

    def handle_rule_phono(self, rule):
        print("Phono received: ", rule)
        self.ruleReceived.emit(rule)
        self.accept()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    UiWindow = UI_Main()
    app.exec_()
