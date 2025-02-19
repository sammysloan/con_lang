from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.initUI()
        self.setGeometry(200, 200, 600, 600)
        self.setWindowTitle("GUI test")

    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("I don't really know what is going on.")
        self.label.move(10, 10)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Click me ")
        self.b1.move(100, 100)
        self.b1.clicked.connect(self.clicked)
    
    def clicked(self):
        self.label.setText("the button was click-ed")
        self.update()

    def update(self):
        self.label.adjustSize()




def window():
    app = QApplication(sys.argv)
    win = MyWindow()




    win.show()
    sys.exit(app.exec_())

window()