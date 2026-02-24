import json, sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QInputDialog, QTableWidgetItem, QMenu, QAbstractItemView
from PyQt5.QtCore import Qt

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORTHO_DB_PATH = os.path.join(BASE_DIR, "presets", "orthographies.db")
DB_PATH = "presets/presets.db"

PLACEHOLDER_ORTHO = "<New orthography>"


class OrthographyEditor(QDialog):
    def __init__(self, parent=None, start_preset=None):
        super().__init__(parent)
        uic.loadUi("interface/orthographer.ui", self)


        self.combo = self.comboBox_preset
        self.table = self.tableWidget_ortho
        self.table.setColumnWidth(0, 300)
        self.table.setColumnWidth(1, 300)
        

        self.pushButton_save.clicked.connect(self.save)
        self.pushButton_save_as.clicked.connect(self.save_as)
        self.pushButton_rename.clicked.connect(self.rename)
        self.pushButton_delete.clicked.connect(self.delete)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.combo.currentTextChanged.connect(self.load_preset)

        self.ensure_table_exists()
        self.populate_combo()

        if start_preset:
            idx = self.combo.findText(start_preset)
            self.combo.setCurrentIndex(idx if idx != -1 else 0)
        else:
            self.combo.setCurrentIndex(0)

        # Table behavior: 2 columns, editable cells, row selection
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["IPA", "Orthography"])
        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)

        # Keep a trailing blank row so users can just type to add a new mapping
        self.table.itemChanged.connect(self._ensure_blank_trailing_row)
        self.table.cellChanged.connect(self._ensure_blank_trailing_row)

        # Context menu: Add / Delete rows
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._table_menu)

        # Start with one blank row
        if self.table.rowCount() == 0:
            self._insert_blank_row()

    # --- Table helpers ---
    
    def _row_is_empty(self, r: int) -> bool:
        def _txt(c):
            it = self.table.item(r, c)
            return "" if it is None else it.text().strip()
        return _txt(0) == "" and _txt(1) == ""

    def _ensure_blank_trailing_row(self, *_):
        """Ensure there is always one empty row at the end; add one if needed."""
        rcount = self.table.rowCount()
        if rcount == 0:
            self._insert_blank_row()
            return
        if not self._row_is_empty(rcount - 1):
            self._insert_blank_row()

    def _table_menu(self, pos):
        menu = QMenu(self)
        add_act = menu.addAction("Add row")
        del_act = menu.addAction("Delete selected row(s)")
        action = menu.exec_(self.table.viewport().mapToGlobal(pos))
        if action is add_act:
            self.table.insertRow(self.table.rowCount())
        elif action is del_act:
            rows = sorted({idx.row() for idx in self.table.selectedIndexes()}, reverse=True)
            # Don't delete the trailing blank if it's the only row
            for r in rows:
                if self.table.rowCount() > 1:
                    self.table.removeRow(r)
        self._ensure_blank_trailing_row()

    def _commit_pending_edits(self):
        """
        Force-commit any active editor so QTableWidgetItem holds the latest text.
        """
        # Move focus away from the editor to trigger the delegate's commit
        self.table.setFocus(Qt.OtherFocusReason)

        # If there is a persistent editor open, close it (belt-and-suspenders)
        itm = self.table.currentItem()
        if itm is not None:
            self.table.closePersistentEditor(itm)
    
    def _insert_blank_row(self, pos=None):
        r = self.table.rowCount() if pos is None else pos
        self.table.insertRow(r)
        # seed empty items so edits always trigger signals
        if self.table.item(r, 0) is None:
            self.table.setItem(r, 0, QTableWidgetItem(""))
        if self.table.item(r, 1) is None:
            self.table.setItem(r, 1, QTableWidgetItem(""))
        return r

    # --- DB helpers ---
    def ensure_table_exists(self):
        with sqlite3.connect(ORTHO_DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS orth_presets (name TEXT PRIMARY KEY, data TEXT)")
            conn.commit()

    

    def populate_combo(self):
        self.combo.clear()
        self.combo.addItem(PLACEHOLDER_ORTHO)  # placeholder for creating a new one
        with sqlite3.connect(ORTHO_DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS orth_presets (name TEXT PRIMARY KEY, data TEXT)")
            cur.execute("SELECT name FROM orth_presets ORDER BY name COLLATE NOCASE")
            for (name,) in cur.fetchall():
                self.combo.addItem(name)


    # --- Table IO ---
    def load_preset(self, name):
        self.table.setRowCount(0)
        if not name or name == PLACEHOLDER_ORTHO:
            # one seeded blank row so editing works and signals fire
            self._insert_blank_row()
            return
        
        with sqlite3.connect(ORTHO_DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT data FROM orth_presets WHERE name=?", (name,))
            row = cur.fetchone()
        if not row:
            return
        try:
            mapping = json.loads(row[0]).get("map", [])
            for ipa, ortho in mapping:
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(ipa))
                self.table.setItem(r, 1, QTableWidgetItem(ortho))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load orthography: {e}")
        
        self._ensure_blank_trailing_row()
        self._insert_blank_row()

    def read_table(self):
        mapping = []
        for r in range(self.table.rowCount()):
            ipa = self.table.item(r, 0)
            ortho = self.table.item(r, 1)
            ipa_val = ipa.text().strip() if ipa else ""
            ortho_val = ortho.text().strip() if ortho else ""
            if ipa_val and ortho_val:
                mapping.append([ipa_val, ortho_val])
        mapping.sort(key=lambda x: len(x[0]), reverse=True)  # greedy
        return mapping

    # --- Buttons ---
    def save(self):
        self._commit_pending_edits()
        name = self.combo.currentText().strip()
        if not name or name == PLACEHOLDER_ORTHO:
            self.save_as()
            return
        self._write_preset(name)
        self._ensure_blank_trailing_row()

    def save_as(self):
        name, ok = QInputDialog.getText(self, "Save As", "Preset name:")
        if not ok or not name.strip():
            return
        self._write_preset(name.strip())
        self.populate_combo()
        self.combo.setCurrentText(name.strip())
        self._ensure_blank_trailing_row()

    def rename(self):
        old = self.combo.currentText()
        if not old:
            return
        new, ok = QInputDialog.getText(self, "Rename", "New name:", text=old)
        if not ok or not new.strip() or new == old:
            return
        new = new.strip()
        with sqlite3.connect(ORTHO_DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE orth_presets SET name=? WHERE name=?", (new, old))
            conn.commit()
        self.populate_combo()
        self.combo.setCurrentText(new)

    def delete(self):
        name = self.combo.currentText()
        if not name:
            return
        if QMessageBox.question(self, "Delete", f"Delete '{name}'?") != QMessageBox.Yes:
            return
        with sqlite3.connect(ORTHO_DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM orth_presets WHERE name=?", (name,))
            conn.commit()
        self.populate_combo()
        self.table.setRowCount(0)

    def _write_preset(self, name):
        self._commit_pending_edits()
        payload = json.dumps({"map": self.read_table()}, ensure_ascii=False)
        with sqlite3.connect(ORTHO_DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO orth_presets (name, data) VALUES (?, ?)", (name, payload))
            conn.commit()
