import Config

from PyQt5 import QtCore, QtWidgets, QtGui


class About(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        mainLayout = QtWidgets.QVBoxLayout()

        htmlString="<html><head/><body><p align=\"center\"><span style=\" font-size:28pt; font-weight:600;\">xCite Citation Manager</span></p><p align=\"center\"><br/></p><p align=\"center\">Developed By: Benjamin Atkerson, 2022</p><p><br/>Contributors:</p><p>Ward, Alex -</p><p>Atkerson, Benjamin -</p><p>Buckley, David -</p><p>Chabre, Derek -</p><p>Glazier, Leah -</p></body></html>"



        textLabel=QtWidgets.QLabel()
        textLabel.setText(htmlString)

        mainLayout.addWidget(textLabel)

        self.setLayout(mainLayout)


        self.setFixedSize(600,400)
        self.show()

