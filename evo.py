from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QComboBox, 
                             QDialog, QDialogButtonBox, QLineEdit, QListWidget,
                             QPushButton, QRadioButton, QTextEdit)
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic
import sys

class UI_Main(QMainWindow):
    def __init__(self):
        super(UI_Main, self).__init__()
        uic.loadUi("evo.ui", self)

        # Define out widgets
        self.button_save = self.findChild(QPushButton, "pushButton_save")
        self.combo_select = self.findChild(QComboBox, "comboBox_preset")
        self.button_phono = self.findChild(QPushButton, "pushButton_phono")
        self.button_lexi = self.findChild(QPushButton, "pushButton_lexi" )
        self.button_gram = self.findChild(QPushButton, "pushButton_gram")
        self.button_edit = self.findChild(QPushButton, "pushButton_edit")
        self.button_remove = self.findChild(QPushButton, "pushButton_remove")
        self.button_clear = self.findChild(QPushButton, "pushButton_clear")
        self.list_widget = self.findChild(QListWidget, "listWidget")

        self.list_rule = []

        # Initialization functions
        self.button_phono.clicked.connect(self.addRule)
        
        # Show the app
        self.show()

    def addRule(self):
        self.dialog_phono = UI_Phono()
        # Checks for ruleReceived signal from phono; calls handle func
        self.dialog_phono.ruleReceived.connect(self.handle_rule_main)
        self.dialog_phono.exec_()
        

    def handle_rule_main(self, rule):
        print("Main received", rule)



        # self.list_rule.append(self.dialog_phono.rule)
        print(self.list_rule)

class UI_Assimilate(QDialog):
    ruleSent = pyqtSignal(list) # Signal to dialog_phono that rule sent

    def __init__(self):
        super(UI_Assimilate, self).__init__()
        uic.loadUi("dialog_assimilate.ui", self)

        # Define widgets
        self.lineEdit_name = self.findChild(QLineEdit, "lineEdit_name") 
        self.lineEdit_target_list = self.findChild(QLineEdit, "lineEdit_target")
        self.lineEdit_trigger = self.findChild(QLineEdit, "lineEdit_trigger")
        self.checkBox_prog = self.findChild(QCheckBox, "checkBox_prog")
        self.checkBox_skip = self.findChild(QCheckBox, "checkBox_skip")
        self.button_close = self.findChild(QPushButton, "pushButton_close")
        self.button_save = self.findChild(QPushButton, "pushButton_save")

        # Add functionality
        self.button_save.clicked.connect(self.make_rule)

    def make_rule(self):

        # Setup required inputs

class UI_Context(QDialog):
    ruleSent = pyqtSignal(list) # Signal to dialog_phono that rule sent

    def __init__(self):
        super(UI_Context, self).__init__()
        uic.loadUi("dialog_context.ui", self)

        # Define widgets
        self.lineEdit_name = self.findChild(QLineEdit, "lineEdit_name") 
        self.lineEdit_old_list = self.findChild(QLineEdit, "lineEdit_old_list")
        self.lineEdit_new_list = self.findChild(QLineEdit, "lineEdit_new_list")
        self.checkBox_solo = self.findChild(QCheckBox, "checkBox_solo")
        self.checkBox_skip = self.findChild(QCheckBox, "checkBox_skip")
        self.lineEdit_pre_ex = self.findChild(QLineEdit, "lineEdit_pre_ex")
        self.lineEdit_post_ex = self.findChild(QLineEdit, "lineEdit_post_ex")
        self.lineEdit_pre_trig = self.findChild(QLineEdit, "lineEdit_pre_trig")
        self.lineEdit_post_trig = self.findChild(QLineEdit, "lineEdit_post_trig")
        self.textEdit_notes = self.findChild(QTextEdit, "textEdit_notes")
        self.button_close = self.findChild(QPushButton, "pushButton_close")
        self.button_save = self.findChild(QPushButton, "pushButton_save")

        # Add functionality
        self.button_save.clicked.connect(self.make_rule)

    def make_rule(self):

        # Setup required inputs
        if self.lineEdit_name.text() and self.textEdit_notes.toPlainText():
            name = self.lineEdit_name.text()
            notes = self.textEdit_notes.toPlainText()
        else: 
            print("No name or notes given. Add to continue.")
            return # This may not be correct keyword to break method. CHECK

        if not self.lineEdit_new_list.text():
            print("No new values given. Add to continue.")
            return # This may not be correct keyword to break method.
        else: new_list = self.lineEdit_new_list.text().split()

        # Setup checkBox functionality
        if self.checkBox_skip.isChecked() == True:
            stress_skip = True
        else: stress_skip = False
        if self.checkBox_solo.isChecked() == True:
            stress_solo = True
        else: stress_solo = False

        # Setup lineEdit functionality
        old_list = self.lineEdit_old_list.text().split()
        pre_ex = self.lineEdit_pre_ex.text().split()
        post_ex = self.lineEdit_post_ex.text().split()
        pre_trig = self.lineEdit_pre_trig.text().split()
        post_trig = self.lineEdit_post_trig.text().split()

        rule = ["context", name, notes, old_list, new_list, pre_ex, post_ex, 
                pre_trig, post_trig, stress_skip, stress_solo]
        
        self.send_rule(rule)
        
    def send_rule(self, rule):
        print("Func called", rule)
        self.ruleSent.emit(rule)
        self.accept()


class UI_Phono(QDialog):
    # Signal that rule was recieved and sends to main
    ruleReceived = pyqtSignal(list)

    def __init__(self):
        super(UI_Phono, self).__init__()
        uic.loadUi("dialog_phono.ui", self)

        # Define widgets
        self.ass = self.findChild(QRadioButton, "radioButton_ass")
        self.con = self.findChild(QRadioButton, "radioButton_con")
        self.syll = self.findChild(QRadioButton, "radioButton_syll")
        self.button_close = self.findChild(QPushButton, "pushButton_close")
        self.button_create = self.findChild(QPushButton, "pushButton_create")


        self.button_create.clicked.connect(self.select_type)

    def select_type(self): 
        if self.ass.isChecked() == True:
            print("Add dialog")
        elif self.con.isChecked() == True:
            self.dialog_context = UI_Context()
            # Checks for ruleSent signal from context; calls handle func
            self.dialog_context.ruleSent.connect(self.handle_rule_phono)
            self.dialog_context.exec_()

    def handle_rule_phono(self, rule):
        print("Phono received: ", rule)
        self.ruleReceived.emit(rule)
        self.accept()

# Initialize the app
app = QApplication(sys.argv)
UiWindow = UI_Main()
app.exec_()

# Next steps: figure out how to handle and save all the data from UI_Context