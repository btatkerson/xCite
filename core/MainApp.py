#!/usr/bin/python3

import sys
sys.path.insert(0, './core')

from Config import *
from InputForm import InputForm
from LabeledWidgets import LabeledWidget
from FormattedDisplay import FormattedDisplay as CitationPane
from RecordSheet import RecordSheet
from About import About

import CitationManagement

from PyQt5 import QtCore, QtWidgets, QtGui

FOR_WINDOWS = True

# This will be the master window the application.
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, appWidget=None):
        super().__init__()
        self.app = appWidget
        CitationManagement.mainCiteManager.setOutput(self.setMessageBox)
        
        self.setWindowTitle("xCite Citation Manager")
        #self.setWindowTitle(choice(VALID_APPLICATION_TITLES))
        self.setMinimumWidth(MinWindowWidth)
        self.setMinimumHeight(MinWindowHeight)

        self.resize(DefaultWindowSize[0],DefaultWindowSize[1])

        self.newFileButton = QtWidgets.QPushButton("New File")
        self.saveFileButton = QtWidgets.QPushButton("Save File")
        self.saveAsFileButton = QtWidgets.QPushButton("Save As File")
        self.openFileButton = QtWidgets.QPushButton("Open File")

        
        fileMenu=self.menuBar().addMenu("&File")
        aboutMenu=self.menuBar().addMenu("About")
        
        newAction = QtWidgets.QAction('&New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New Database')
        newAction.triggered.connect(self.openFile)

        openAction = QtWidgets.QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open Database')
        openAction.triggered.connect(self.openFile)

        saveAction = QtWidgets.QAction('&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save Database')
        saveAction.triggered.connect(self.saveFile)

        saveAsAction = QtWidgets.QAction('Save As', self)
        saveAsAction.setShortcut('Ctrl+Shift+S')
        saveAsAction.setStatusTip('Save Database As')
        saveAsAction.triggered.connect(self.saveAsFile)

        aboutAction = QtWidgets.QAction('About', self)
        aboutAction.setStatusTip('About')
        aboutAction.triggered.connect(self.aboutXcite)
        
        fileMenu.addActions([newAction, openAction, saveAction, saveAsAction])
        aboutMenu.addActions([aboutAction])
        #exitAction.triggered.connect(qApp.quit)


        self.buttonHeaderBar = QtWidgets.QHBoxLayout()
        self.buttonHeaderBar.addWidget(self.newFileButton)
        self.buttonHeaderBar.addWidget(self.saveFileButton)
        self.buttonHeaderBar.addWidget(self.saveAsFileButton)
        self.buttonHeaderBar.addWidget(self.openFileButton)

        self.newFileButton.clicked.connect(self.newFile)
        self.saveFileButton.clicked.connect(self.saveFile)
        self.saveAsFileButton.clicked.connect(self.saveAsFile)
        self.openFileButton.clicked.connect(self.openFile)
        
        self.tabInputCitation = QtWidgets.QTabWidget()


        self.dialogueLineEdit = LabeledWidget(DIALG, "Sys Messages:", DefaultLabelWidthColA, parent=self)
        self.dialogueLineEdit.setWidget(QtWidgets.QTextBrowser())

        self.dialogueLineEdit.getContent=self.dialogueLineEdit.getWidget().toHtml
        self.dialogueLineEdit.setText=self.dialogueLineEdit.getWidget().setHtml
        self.dialogueLineEdit.setContent=self.dialogueLineEdit.setText
        self.dialogueLineEdit.getWidget().setReadOnly(True)
        self.dialogueLineEdit.setFixedHeight(DefaultMessageBoxHeight)
        self.dialogueLineEdit.setImportantOn()



        inputWidget = InputForm()
        inputWidget.resizeEvent()
        inputWidget.output = self.setMessageBox
        inputWidget.setCurrentCitation(CitationManagement.mainCiteManager.getCitationByID(0))
        SharedObjects[INPUT] = inputWidget

        citationTab = CitationPane()
        citationTab.output = self.setMessageBox
        self.updateCitations = citationTab.updateDisplay


        self.tabInputCitation.addTab(inputWidget, "Modify Records")
        self.tabInputCitation.addTab(citationTab, "Citations")
        self.tabInputCitation.currentChanged.connect(self.updateCitations)

        tabWidgetLayout = QtWidgets.QVBoxLayout()
        tabWidgetLayout.addLayout(self.buttonHeaderBar)
        tabWidgetLayout.addWidget(self.tabInputCitation)
        tabWidgetLayout.addWidget(self.dialogueLineEdit)

        self.mainRecordSheet = RecordSheet()
        self.mainRecordSheet.output = self.setMessageBox
        #mainRecordSheet.recordList.setInputForm(.inputWidget)

        mainLayout = QtWidgets.QHBoxLayout()
        #mainLayout.addWidget(inputWidget)
        mainLayout.addLayout(tabWidgetLayout)
        mainLayout.addWidget(self.mainRecordSheet)

        mainWidget = QtWidgets.QWidget()
        mainWidget.setLayout(mainLayout)
        

        self.setCentralWidget(mainWidget)    
        inputWidget.titleInput.getWidget().setFocus()

        self.__currentFile = None

        '''
        inputWidget.setTabOrder(inputWidget.accessDateEdit.getWidget(), inputWidget.titleInput.getWidget())
        inputWidget.setTabOrder(inputWidget.titleInput.getWidget(), inputWidget.contentTypeComboBoxInput.getWidget())
        inputWidget.setTabOrder(inputWidget.contentTypeComboBoxInput.getWidget(),inputWidget.authorTable.tableAuthorCount.getWidget())

        '''

    def openModifyTab(self):
        self.tabInputCitation.setCurrentIndex(0)

    def openCitationTab(self):
        self.tabInputCitation.setCurrentIndex(1)

    def openFile(self):
        #fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open xCite Database","./User Databases","xCite Database File (.xct)")
        if FOR_WINDOWS:
            fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open xCite Database","./User Databases")
        else:
            fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open xCite Database","./User Databases","xCite Database File (.xct)")
        print("File:",fileName)

        if fileName[0]:
            CitationManagement.mainCiteManager.readInDatabaseFromFile(fileName[0])
            self.mainRecordSheet.recordList.setCurrentCitations()
            SharedObjects[INPUT].setCurrentCitation(CitationManagement.mainCiteManager.getCitationByID(0))
            self.__currentFile = fileName[0]
            self.setWindowTitle("xCite Citation Manager - %s"%(fileName[0].split("/")[-1]))
            self.updateCitations()

    def saveFile(self):
        if self.__currentFile:
            if CitationManagement.mainCiteManager.containsOneValidRecord():
                SharedObjects[INPUT].saveCurrentCitation()
                CitationManagement.mainCiteManager.writeCitationsToDatabase(self.__currentFile)
            else:
                emptyF = open(DefaultCleanFile,'r')
                emptyFText = emptyF.read()
                emptyF.close()

                currentF = open(self.__currentFile, 'w')
                currentF.write(emptyFText)
                currentF.close()
                


        else:
            #fileName = QtWidgets.QFileDialog.getSaveFileName(self, "Save xCite Database","./User Databases","xCite Database File (.xct)")

            if FOR_WINDOWS:
                fileName = QtWidgets.QFileDialog.getSaveFileName(self, "Save xCite Database","./User Databases")
            else:
                fileName = QtWidgets.QFileDialog.getSaveFileName(self, "Save xCite Database","./User Databases","xCite Database File (.xct)")

            if fileName[0]:
                self.__currentFile = fileName[0]
                if not self.__currentFile.endswith(".xct"):
                    self.__currentFile+=".xct"
                if CitationManagement.mainCiteManager.containsOneValidRecord():
                    CitationManagement.mainCiteManager.writeCitationsToDatabase(self.__currentFile)
                else:
                    emptyF = open(DefaultCleanFile,'r')
                    emptyFText = emptyF.read()
                    emptyF.close()

                    currentF = open(self.__currentFile, 'w')
                    currentF.write(emptyFText)
                    currentF.close()
                    
        self.setWindowTitle("xCite Citation Manager - %s"%(self.__currentFile.split("/")[-1]))

    def saveAsFile(self):
        if self.__currentFile:
            if FOR_WINDOWS:
                fileName = QtWidgets.QFileDialog.getSaveFileName(self, "Save xCite Database As",self.__currentFile)
            else:
                fileName = QtWidgets.QFileDialog.getSaveFileName(self, "Save xCite Database As",self.__currentFile,"xCite Database File (.xct)")
            #fileName = QtWidgets.QFileDialog.getSaveFileName(self, "Save xCite Database As",self.__currentFile,"xCite Database File (.xct)")
        else:
            if FOR_WINDOWS:
                fileName = QtWidgets.QFileDialog.getSaveFileName(self, "Save xCite Database As","./User Databases/NewDatabase.xct")
            else:
                fileName = QtWidgets.QFileDialog.getSaveFileName(self, "Save xCite Database As","./User Databases/NewDatabase.xct","xCite Database File (.xct)")
            #fileName = QtWidgets.QFileDialog.getSaveFileName(self, "Save xCite Database As","./User Databases/NewDatabase.xct","xCite Database File (.xct)")

            
        if fileName[0]:
            self.__currentFile = fileName[0]
            self.saveFile()

    def newFile(self):
        if FOR_WINDOWS:
            fileName = QtWidgets.QFileDialog.getSaveFileName(self, "New xCite Database","./User Databases/NewDatabase.xct")
        else:
            fileName = QtWidgets.QFileDialog.getSaveFileName(self, "New xCite Database","./User Databases/NewDatabase.xct","xCite Database File (.xct)")
        #fileName = QtWidgets.QFileDialog.getSaveFileName(self, "New xCite Database","./User Databases/NewDatabase.xct","xCite Database File (.xct)")

        if fileName[0]:
            CitationManagement.mainCiteManager.readInDatabaseFromFile(newfile=True)
            self.mainRecordSheet.recordList.setCurrentCitations()
            SharedObjects[INPUT].setCurrentCitation(CitationManagement.mainCiteManager.getCitationByID(0))
            self.__currentFile = fileName[0]
            self.setWindowTitle("xCite Citation Manager - %s"%(fileName[0].split("/")[-1]))
            
    def aboutXcite(self):
        ab=About(self)
        ab.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        ab.setWindowTitle("About xCite")
        ab.show()
            
        


    def setMessageBox(self, message, bold=None, italic=False, underline=None, color=None, append=False):
        newStr = message

        if bold:
            newStr = "<b>"+newStr+"</b>"
        if italic:
            newStr = "<i>"+newStr+"</i>"
        if underline:
            newStr = "<u>"+newStr+"</u>"
        if color:
            newStr = "<font color=%s>"%(color)+newStr+"</font>"

        if not append:
            self.dialogueLineEdit.setText(newStr)
        else:
            if self.dialogueLineEdit.getWidget().toPlainText() == "":
                self.dialogueLineEdit.setText(newStr)
            else:
                self.dialogueLineEdit.setText(self.dialogueLineEdit.getWidget().toHtml()+newStr)
        self.dialogueLineEdit.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus | QtCore.Qt.FocusPolicy.ClickFocus)
        #self.dialogueLineEdit.getWidget().setEditable(False)
        #QtWidgets.QTextBrowser.set






def main():
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow(app)
    window.show()

    sys.exit(app.exec_())

