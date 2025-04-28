from PyQt5.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QLineEdit, QTextEdit
from PyQt5 import uic

class Ui_DialogContext(QDialog):
    def __init__(self):
        super(Ui_DialogContext, self).__init__()

        # Load UI
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
        self.buttonBox = self.findChild(QDialogButtonBox, "buttonBox")

        # Show the app
        self.show()

    def add_data(self):
        # Get input
        name = self.lineEdit_name.text()
        old_list = self.lineEdit_old_list.text()
        new_list = self.lineEdit_new_list.text()

        # Pass inputs to main window

app = QDialog()
DialogContext = Ui_DialogContext()
app.exec_()
