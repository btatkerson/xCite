import datetime
from Config import *
import LabeledWidgets

import CitationManagement
from PyQt5 import QtCore, QtWidgets, QtGui

CitMan = CitationManagement.mainCiteManager

class RecordSheet(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)

        self.recordList = RecordList()
        self.setMinimumWidth(400)

        self.filterTitle = LabeledWidgets.LabeledTextBox(FILTI,"Title:", DefaultFilterLabelText)
        self.filterLastName = LabeledWidgets.LabeledTextBox(FILLN,"Last Name:",DefaultFilterLabelText)
        self.filterFirstName = LabeledWidgets.LabeledTextBox(FILFN,"First Name:",DefaultFilterLabelText)
        self.filterMiddleInit = LabeledWidgets.LabeledTextBox(FILMI,"Middle Init:",DefaultFilterLabelText, None, 1)

        self.contentTypeComboBoxInput = LabeledWidgets.LabeledComboBox(TYPEF, "Type of Content:", ["",TYPE_ARTICLE, TYPE_BOOK, TYPE_CONFERENCE_PAPER], DefaultFilterLabelText)

        self.exactMatchFilter = LabeledWidgets.LabeledWidget(EXCTF,"Exact Match:",DefaultFilterLabelText)
        self.exactMatchFilter.setWidget(QtWidgets.QCheckBox())

        self.enableFiltersCheck = LabeledWidgets.LabeledWidget(ENBLF,"Enable Filters:",DefaultFilterLabelText)
        self.enableFiltersCheck.setWidget(QtWidgets.QCheckBox())
        

        self.filterTitle.getTextBox().textEdited.connect(self.applyFilterChanges)
        self.filterLastName.getTextBox().textEdited.connect(self.applyFilterChanges)
        self.filterFirstName.getTextBox().textEdited.connect(self.applyFilterChanges)
        self.filterMiddleInit.getTextBox().textEdited.connect(self.applyFilterChanges)
        self.contentTypeComboBoxInput.getWidget().currentIndexChanged.connect(self.applyFilterChanges)
        self.exactMatchFilter.getWidget().toggled.connect(self.applyFilterChanges)
        self.enableFiltersCheck.getWidget().toggled.connect(self.applyFilterChanges)

        self.expandButton = QtWidgets.QPushButton("Expand Records")
        self.collapseButton = QtWidgets.QPushButton("Collapse Records")
        self.clearFiltersButton = QtWidgets.QPushButton("Clear Filters")

        self.expandButton.clicked.connect(lambda x:self.recordList.expandAll())
        self.collapseButton.clicked.connect(lambda x:self.recordList.collapseAll())
        self.clearFiltersButton.clicked.connect(lambda x: self.clearFilters())

        filterHeaderLayout = QtWidgets.QHBoxLayout()
        filterHeaderLayout.addWidget(self.expandButton)
        filterHeaderLayout.addWidget(self.collapseButton)
        filterHeaderLayout.addWidget(self.clearFiltersButton)

        mainLayout.addWidget(self.recordList)

        mainLayout.addLayout(filterHeaderLayout)
        mainLayout.addWidget(self.enableFiltersCheck)
        mainLayout.addWidget(self.contentTypeComboBoxInput)
        mainLayout.addWidget(self.filterTitle)
        mainLayout.addWidget(self.filterLastName)
        mainLayout.addWidget(self.filterFirstName)
        mainLayout.addWidget(self.filterMiddleInit)
        mainLayout.addWidget(self.exactMatchFilter)

        self.applyFilterChanges()


    def isContentTypeFiltered(self):
        if self.contentTypeComboBoxInput.getContent() == 0:
            return False
        return True

    def getContentTypeFilter(self):
        return self.contentTypeComboBoxInput.getIndex()

    def isTitleFiltered(self):
        if self.filterTitle.getText() == "":
            return False
        return True

    def getTitleFilter(self):
        return self.filterTitle.getText() 

    def isLastNameFiltered(self):
        if self.filterLastName.getText() == "":
            return False
        return True

    def getLastNameFilter(self):
        return self.filterLastName.getText() 

    def isFirstNameFiltered(self):
        if self.filterFirstName.getText() == "":
            return False
        return True

    def getFirstNameFilter(self):
        return self.filterFirstName.getText() 

    def isMiddleInitFiltered(self):
        if self.filterMiddleInit.getText() == "":
            return False
        return True

    def getMiddleInitFilter(self):
        return self.filterMiddleInit.getText() 

    def isExactMatch(self):
        return self.exactMatchFilter.getWidget().isChecked()

    def clearFilters(self):
        #self.enableFiltersCheck.getWidget().setChecked(False)
        self.contentTypeComboBoxInput.getWidget().setCurrentIndex(0)
        self.filterTitle.getWidget().setText("")
        self.filterLastName.getWidget().setText("")
        self.filterFirstName.getWidget().setText("")
        self.filterMiddleInit.getWidget().setText("")
        self.exactMatchFilter.getWidget().setChecked(False)
    
    def applyFilterChanges(self):
        CitMan.setFilter(TYPEF,self.getContentTypeFilter())
        CitMan.setFilter(FILTI,self.getTitleFilter())
        CitMan.setFilter(FILLN,self.getLastNameFilter())
        CitMan.setFilter(FILFN,self.getFirstNameFilter())
        CitMan.setFilter(FILMI,self.getMiddleInitFilter())
        CitMan.setFilter(EXCTF,self.isExactMatch())


        if not self.enableFiltersCheck.getWidget().isChecked():
            self.contentTypeComboBoxInput.setDisabled(True)
            self.filterTitle.setDisabled(True)
            self.filterLastName.setDisabled(True)
            self.filterFirstName.setDisabled(True)
            self.filterMiddleInit.setDisabled(True)
            self.exactMatchFilter.setDisabled(True)

            CitMan.setFiltersEnabled(False)

        else:
            self.contentTypeComboBoxInput.setDisabled(False)
            self.filterTitle.setDisabled(False)
            self.filterLastName.setDisabled(False)
            self.filterFirstName.setDisabled(False)
            self.filterMiddleInit.setDisabled(False)
            self.exactMatchFilter.setDisabled(False)

            CitMan.setFiltersEnabled()

        SharedObjects[CTDSP].updateDisplay()
        
        



        self.recordList.setCurrentCitations()

 
class RecordList(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        labelWidget = LabeledWidgets.LabeledWidget(RECRD, labelText="", fixedLabelWidth=None, fixedWidgetWidth=None, parent=parent)

        labelWidget.setWidget(self)


        self.setColumnCount(6)
        self.setHeaderLabels(["ID", "Title", "Last Name", "First Name", "M.I.", "Type of Content"])
        self.setColumnWidth(0, 20)
        self.setColumnWidth(1, 200)
        self.setColumnWidth(2, 200)
        self.setColumnWidth(3, 200)
        self.setColumnWidth(4, 20)

        self.citationManager = CitationManagement.mainCiteManager
        self.setCurrentCitations()

        self.itemSelectionChanged.connect(self.onIndexChange)

        self.staticIndex = -1
        #self.setDragEnabled(False)
        self.__inputForm = None




    def setInputForm(self, inputForm):
        self.__inputForm = inputForm


    def setCurrentCitations(self):
        '''
        Sets the input forms to match what's in the current citation object
        '''
        self.clear()
        #cites = self.citationManager.getCurrentDictOfCitations()
        cites = self.citationManager.getCurrentDictOfFilteredCitations()


        #for i in sorted(cites, key=lambda x: cites[x].getAuthorByIndex(0)[LNAME]):
        for i in sorted(cites):

            #if cites[i].isCitationSet():
            #if cites[i].getTypeOfContent()==TYPE_ARTICLE:

            auth = cites[i].getAuthorByIndex(0)

            self.addTopLevelItem(QtWidgets.QTreeWidgetItem([str(i+1),cites[i].getTitle(),auth[LNAME],auth[FNAME],auth[MINIT],cites[i].getTypeOfContent()]))

            for j in range(cites[i].getNumberOfAuthors() - 1):
                auth = cites[i].getAuthorByIndex(j+1)
                self.topLevelItem(self.topLevelItemCount()-1).addChild(QtWidgets.QTreeWidgetItem(self.topLevelItem(self.topLevelItemCount()-1),["","",auth[LNAME],auth[FNAME],auth[MINIT],""]))
 

            
    def refreshText(self):

        for i in range(self.topLevelItemCount()):
            newInd = int(self.topLevelItem(i).text(0))-1
            cite = CitationManagement.mainCiteManager.getCitationByID(newInd)
            auth = cite.getAuthorByIndex(0)

            self.topLevelItem(i).setText(0,str(newInd+1))
            self.topLevelItem(i).setText(1,cite.getTitle())
            self.topLevelItem(i).setText(2,auth[LNAME])
            self.topLevelItem(i).setText(3,auth[FNAME])
            self.topLevelItem(i).setText(4,auth[MINIT])
            self.topLevelItem(i).setText(5,cite.getTypeOfContent())
            
            for j in range(cite.getNumberOfAuthors() - 1):
                auth = cite.getAuthorByIndex(j+1)
                child = self.topLevelItem(i).child(j)

                child.setText(0,"")
                child.setText(1,"")
                child.setText(2,auth[LNAME])
                child.setText(3,auth[FNAME])
                child.setText(4,auth[MINIT])
                child.setText(5,"")
                



    def onIndexChange(self, e=None):
        #print("CHANGED!",self.currentItem(), self.indexOfTopLevelItem(self.currentItem()))
        

        # Not working right
        if SharedObjects[ATOSV].isChecked():
            SharedObjects[INPUT].saveCurrentCitation()

        
        SharedObjects[INPUT].output("")

        item = self.currentItem()

        if not item:
            return 
        parentItem = None
        if item.parent():
            parentItem = item.parent()
            item = parentItem


        index = int(self.topLevelItem(self.indexOfTopLevelItem(item)).text(0))-1

        
        #SharedObjects[INPUT].saveCurrentCitation(CitationManagement.mainCiteManager.getCitationByID(index))
        SharedObjects[INPUT].setCurrentCitation(CitationManagement.mainCiteManager.getCitationByID(index))


        self.refreshText()
            
        #SharedObjects[INPUT].setCurrentCitation(CitationManagement.mainCiteManager.getCitationByID(index))

