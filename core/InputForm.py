#!/usr/bin/python3

import datetime
from Config import *
import LabeledWidgets

import CitationManagement
CiteMan = CitationManagement.mainCiteManager

from PyQt5 import QtCore, QtWidgets, QtGui

class InputForm(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.output = None
        self.currentCitation = None #CitationManagement.generateEmptyCitationDictionary()

        SharedObjects[INPUT] = self
        

        mainLayout = QtWidgets.QVBoxLayout()

        numericValidator = QtGui.QIntValidator()
        pageValidator = QtGui.QRegExpValidator(QtCore.QRegExp('([0-9]{1,}[ ]{0,1}[,-]{1}[ ]{0,1})*'))
        cityValidator = QtGui.QRegExpValidator(QtCore.QRegExp(
        "[A-Za-z]{1,}[.]{0,1}[ ]{0,1}([A-Za-z]{1,}([ ]{0,1}[-]){0,1}[ ]{0,1})*([A-Za-z]{1}[']{0,1}([A-Za-z]{1,}([ ]{0,1}[-]){0,1}[ ]{0,1})*){0,1}[,]{1}[ ]{0,1}[A-Za-z]{2}"))

        self.lineSeparator = QtWidgets.QFrame()
        self.lineSeparator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.lineSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        #self.lineSeparator.setFixedWidth(600)
        #self.lineSeparator.setFixedHeight(20)

        
        self.saveRecordButton = QtWidgets.QPushButton("Save Record")
        self.cancelButton = QtWidgets.QPushButton("Clear Changes")
        self.newRecordButton = QtWidgets.QPushButton("New Record")
        self.deleteRecordButton = QtWidgets.QPushButton("Delete Record")
        self.autoSaveCheck = QtWidgets.QCheckBox("Auto Save:")
        self.autoSaveCheck.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.autoSaveCheck.setFixedWidth(DefaultLabelWidthColA+38)
        self.autoSaveCheck.hide()
        SharedObjects[ATOSV] = self.autoSaveCheck


        # Prepare the content type combobox and set it to have the initial focus since it will be the first category
        self.contentTypeComboBoxInput = LabeledWidgets.LabeledComboBox(TYPE, "Type of Content:", [TYPE_ARTICLE, TYPE_BOOK, TYPE_CONFERENCE_PAPER], DefaultLabelWidthColA)
        self.contentTypeComboBoxInput.comboBox.currentIndexChanged.connect(self.contentTypeSwitch)
        self.contentTypeComboBoxInput.comboBox.setCurrentIndex(0)
        
        #self.contentTypeComboBoxInput.getComboBox().setFocus()


        # Create appropriate content inputs for all the boxes
        self.titleInput = LabeledWidgets.LabeledTextBox(TITLE,"Title:")
        self.authorTable = LabeledWidgets.AuthorTable(AUTHT, 1)
        self.volumeNumInput = LabeledWidgets.LabeledTextBox(VOLUM, "Volume #:", DefaultLabelWidthColA, parent=self)
        self.volumeNumInput.getTextBox().setValidator(numericValidator)
        self.issueNumInput = LabeledWidgets.LabeledTextBox(ISSUE, "Issue #:", DefaultLabelWidthColB,parent=self)
        self.issueNumInput.getTextBox().setValidator(numericValidator)
        self.pagesInput = LabeledWidgets.LabeledTextBox(PAGES, "Pages:", DefaultLabelWidthColA,parent=self)
        self.pagesInput.getTextBox().setValidator(pageValidator)
        self.publicationInput = LabeledWidgets.LabeledTextBox(PBLCA, "Publication:", DefaultLabelWidthColA, parent=self)
        self.publisherInput = LabeledWidgets.LabeledTextBox(PBLSH, "Publisher:", DefaultLabelWidthColA, parent=self)
        
        self.publisherCityInput = LabeledWidgets.LabeledTextBox(PBCTY, "Publisher City:", DefaultLabelWidthColB, parent=self)
        self.publisherCityInput.getTextBox().setValidator(cityValidator)

        self.urlInput = LabeledWidgets.LabeledTextBox(URL, "URL:", DefaultLabelWidthColB, parent=self)
        self.publishedYearSpinBox = LabeledWidgets.LabeledSpinBox(PBLYR, "Publishing Year:", 2000, None, datetime.date.today().year, DefaultLabelWidthColA, None, self)
        self.publishDateEdit = LabeledWidgets.LabeledCalendarWidget(PBLDT, "Publish Date:", None, DefaultLabelWidthColA, None, parent=self)
        self.accessDateEdit = LabeledWidgets.LabeledCalendarWidget(ACCDT, "Access Date:", None, DefaultLabelWidthColB, None, parent=self)

        self.publishDateFormat = LabeledWidgets.LabeledComboBox(PBLDF, "Publish Date Type:", ["No Date", "Year", "Year / Month", "Year / Month / Day"], DefaultLabelWidthColA)
        self.publishDateFormat.getComboBox().setCurrentIndex(3)
        self.publishDateFormat.getComboBox().currentIndexChanged.connect(self.publishDateType)

        
        self.titleAndContentLayout = QtWidgets.QHBoxLayout()
        self.titleAndContentLayout.addWidget(self.titleInput)
        self.titleAndContentLayout.addWidget(self.contentTypeComboBoxInput)



        self.formColumnLayout = LabeledWidgets.LabeledBoxGrid(2,6)
        self.formColumnLayout.addWidget(1, 1, self.volumeNumInput)
        self.formColumnLayout.addWidget(1, 2, self.issueNumInput)
        self.formColumnLayout.addWidget(2, 1, self.pagesInput)
        self.formColumnLayout.addWidget(3, 1, self.publicationInput)
        self.formColumnLayout.addWidget(4, 1, self.publisherInput)
        self.formColumnLayout.addWidget(3, 2, self.publisherCityInput)
        self.formColumnLayout.addWidget(4, 2, self.urlInput)
        self.formColumnLayout.addWidget(5, 1, self.publishDateFormat)
        self.formColumnLayout.addWidget(6, 1, self.publishDateEdit)
        self.formColumnLayout.addWidget(6, 1, self.publishedYearSpinBox)
        self.formColumnLayout.addWidget(6, 2, self.accessDateEdit)

        #self.formColumnLayout.addWidget(6, 2, self.accessDateFormatCombo)
        self.formColumnLayout.setMinimumHeight(206)


        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.autoSaveCheck)
        buttonLayout.addWidget(self.saveRecordButton)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.newRecordButton)
        buttonLayout.addWidget(self.deleteRecordButton)
        #buttonLayout.addWidget(cal)

        mainLayout.addLayout(self.titleAndContentLayout)
        mainLayout.addWidget(self.lineSeparator)
        mainLayout.addWidget(self.authorTable)
        mainLayout.addWidget(self.formColumnLayout)
        mainLayout.addWidget(self.lineSeparator)
        mainLayout.addLayout(buttonLayout)

        self.authorTable.setNextWidgetInTabSequence(self.volumeNumInput.getWidget())
        self.authorTable.setLastWidgetInTabSequence(self.authorTable.tableAuthorCount.getSpinBox())
        self.authorTable.clearTable()
        self.authorTable.table.installEventFilter(self)

        self.accessDateEdit.getContent()

        #self.publishedYearSpinBox.enableCheckBox()
        #self.publishDateEdit.enableCheckBox()


        self.saveRecordButton.clicked.connect(lambda e: [self.saveCurrentCitation(), LabeledWidgetsDict[RECRD].getWidget().setCurrentCitations()])


        self.cancelButton.clicked.connect(lambda e: self.setCurrentCitation(self.currentCitation))

        self.newRecordButton.clicked.connect(lambda e: [self.saveCurrentCitation(), self.setCurrentCitation(CiteMan.newCitation())])

        self.deleteRecordButton.clicked.connect(lambda e: [CiteMan.removeCitation(self.currentCitation), LabeledWidgetsDict[RECRD].getWidget().setCurrentCitations(), self.setCurrentCitation(CiteMan.citations[0]) ])



        #TABORDERING

        

        self.setLayout(mainLayout)
        self.show()

        '''
        LWW = lambda x, y: self.setTabOrder(LabeledWidgets.getWidgetByID(x).getWidget(),LabeledWidgets.getWidgetByID(y).getWidget())

        LWW(ACCDT,TITLE)
        LWW(TITLE, TYPE)
        LWW(TYPE, NOAUT)
        LWW(NOAUT, VOLUM)
        '''


    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress:
            #print("KEY:",event.key())
            if event.key() == QtCore.Qt.Key_Tab:
                self.authorTable.tabLastCelltoNextChildWidget()
                return True
            if event.key() == QtCore.Qt.Key_Backtab:
                self.authorTable.backtabLastCelltoNextChildWidget()
                return True

        return False
        
    
    def resizeEvent(self, event=None):
        self.authorTable.resizeColumnsProportionally()

    def keyPressEvent(self, e):
        #print(e.key())
        if e.key() == QtCore.Qt.Key.Key_Delete:
            if self.focusWidget()==self.authorTable.table:
                self.authorTable.deleteTextInCurrentCell()
        
        if e.key() in [QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter]:
            self.authorTable.enterTextInCurrentCell()

        '''
        if e.key() == QtCore.Qt.Key.Key_Tab:
            if self.authorTable.table == self.focusWidget():
                self.authorTable.tabLastCelltoNextChildWidget()
            self.focusNextChild()
        '''

    def __clearSpecialFormats(self):
        for i in LabeledWidgetsDict:
            if i not in [AUTHT]:
                LabeledWidgetsDict[i].setWarningOff()
                LabeledWidgetsDict[i].setNoteOff()

    def saveCurrentCitation(self, nextCitation=None):
        #LabeledWidgetsDict[TITLE].setWarningOff()
        #LabeledWidgetsDict[TITLE].setNoteOff()

        if LabeledWidgetsDict[TITLE].isWarningOn():
            LabeledWidgetsDict[TITLE].setWarningOff()
            LabeledWidgetsDict[TITLE].setNoteOff()
            self.output("")

        if LabeledWidgetsDict[PBCTY].isNoteOn():
            LabeledWidgetsDict[PBCTY].setNoteOff()


        ########################################################################
        #        This sets the current citation to the values in the input form
        ########################################################################
        self.currentCitation.setCitationInfoByDictionary(self.pullAllContent())
        #self.output("Saved Changes.")

        if nextCitation:
            self.setCurrentCitation(nextCitation)
        else:
            self.setCurrentCitation(self.currentCitation)
            #LabeledWidgets.LabeledWidgetsDict[RECRD].getWidget().setCurrentCitations()

        # Second time to pull warnings where needed
        self.currentCitation.setCitationInfoByDictionary(self.pullAllContent())
        LabeledWidgetsDict[RECRD].getWidget().setCurrentCitations()
        #self.output("Viewing Citation: %s"%(self.currentCitation.getTitle()))


    def pullAllContent(self):
        dictOfValues = {}
        self.authorTable.cleanFieldData()
        self.authorTable.moveBlankRowsToEnd()

        for i in LabeledWidgetsDict:
            if i not in [FILFN, FILLN, FILMI, FILTI, NOAUT, PBLDF, TYPEF, DIALG]:
                dictOfValues[i] = LabeledWidgetsDict[i].getContent()
            #print(i,LabeledWidgetsDict[i].getContent())

        if self.contentTypeComboBoxInput.getComboBox().currentIndex() == 1:
            dictOfValues[LabeledWidgets.PBLDT] = "00/00/0000"
        else:
            dictOfValues[LabeledWidgets.PBLYR] = ""
            monthDayYear = dictOfValues[PBLDT].split("/")

            if self.publishDateFormat.getComboBox().currentIndex() != 3:
                if self.publishDateFormat.getComboBox().currentIndex() == 0:
                    dictOfValues[LabeledWidgets.PBLDT] = "00/00/0000"
                elif self.publishDateFormat.getComboBox().currentIndex() == 1:
                    dictOfValues[LabeledWidgets.PBLDT] = "00/00/" + monthDayYear[2]
                elif self.publishDateFormat.getComboBox().currentIndex() == 2:
                    dictOfValues[LabeledWidgets.PBLDT] = monthDayYear[0]+"/00/" + monthDayYear[2]

        return dictOfValues



    def contentTypeSwitch(self, e=None):
        #comboBoxVal = self.contentTypeComboBoxInput.getComboBox().value()
        #print("CTS",e)
        self.publishDateFormat.setDisabled(False)
        self.publishedYearSpinBox.setDisabled(False)
        self.publicationInput.setDisabled(False)

        if e == 2:
            self.publisherInput.setLabelText("Conference Title:")
            self.publisherCityInput.setLabelText("Location (City, ST):")
            self.publishDateEdit.setLabelText("Conference Date:")
            self.publishDateFormat.setLabelText("Conference Date Type:")
        else:
            self.publisherInput.setLabelText("Publisher:")
            self.publisherCityInput.setLabelText("Publisher City:")
            self.publishDateEdit.setLabelText("Publishing Date:")
            self.publishDateFormat.setLabelText("Publish Date Type:")

        if e == 1:
            #self.issueNumInput.setDisabled(True)
            self.publishDateFormat.setDisabled(True)
            self.publicationInput.setDisabled(True)

            self.issueNumInput.setLabelText("Edition #:")
            self.pagesInput.setLabelText("Page #(s):")
            if self.formColumnLayout.getCurrentShownWidgetInSlot(6,1) != self.publishedYearSpinBox:
                self.formColumnLayout.swapWidgetShowInSlot(6,1)

        else:
            #self.issueNumInput.setDisabled(False)
            self.publishDateFormat.setDisabled(False)
            self.publicationInput.setDisabled(False)

            self.issueNumInput.setLabelText("Issue #:")
            self.pagesInput.setLabelText("Par. #(s):")
            if self.formColumnLayout.getCurrentShownWidgetInSlot(6,1) == self.publishedYearSpinBox:
                self.formColumnLayout.swapWidgetShowInSlot(6,1)

    def publishDateType(self, e=None):
        self.publishDateEdit.setLabelText("Publishing Date:")
        if e == 0:
            self.publishedYearSpinBox.setDisabled(True)
            self.publishDateEdit.setDisabled(True)

        else:
            self.publishedYearSpinBox.setDisabled(False)
            self.publishDateEdit.setDisabled(False)

            if e==1:
                self.publishDateEdit.calendar.setDisplayFormat("yyyy")
                self.publishDateEdit.setLabelText("Publishing Year:")
            elif e==2:
                self.publishDateEdit.calendar.setDisplayFormat("yyyy, MMM")
            else:
                self.publishDateEdit.setDateFormatMode(7)

    def setCurrentCitation(self, citation):
        self.__clearSpecialFormats()
        if isinstance(citation, CitationManagement.Citation):
            self.currentCitation = citation
            
            if citation.isCitationSet():
                if LabeledWidgetsDict[TITLE].isWarningOn():
                    LabeledWidgetsDict[TITLE].setWarningOff()
                    LabeledWidgetsDict[TITLE].setNoteOff()
                    self.output("")

                #if LabeledWidgetsDict[PBCTY].isNoteOn():
                #    LabeledWidgetsDict[PBCTY].setNoteOff()

                ID = CitationManagement.mainCiteManager.getIDByCitation(citation)
                #self.output("Viewing Citation: %s"%(citation.getTitle()),append=True)

            #if citation.getAccessDateYear():
            if citation.getTitle() == "":
                LabeledWidgets.getWidgetByID(TITLE).setContent("")
            else:
                LabeledWidgets.getWidgetByID(TITLE).setContent(citation.getTitle())
            LabeledWidgets.getWidgetByID(TYPE).setContent(citation.getTypeOfContent(1))
            LabeledWidgets.getWidgetByID(AUTHT).setContent(citation.getAuthors())
            LabeledWidgets.getWidgetByID(VOLUM).setContent(citation.getVolume())
            LabeledWidgets.getWidgetByID(ISSUE).setContent(citation.getIssue())
            LabeledWidgets.getWidgetByID(PAGES).setContent(citation.getPages())
            LabeledWidgets.getWidgetByID(PBLCA).setContent(citation.getPublication())
            LabeledWidgets.getWidgetByID(PBLSH).setContent(citation.getPublisher())
            LabeledWidgets.getWidgetByID(PBCTY).setContent(citation.getPublishingCity())
            LabeledWidgets.getWidgetByID(ACCDT).setContent(citation.getAccessDate())
            LabeledWidgets.getWidgetByID(URL).setContent(citation.getURL())

            if citation.getTypeOfContent() == TYPE_BOOK:
                LabeledWidgets.getWidgetByID(PBLYR).setContent(citation.getPublishedYear())
            else:
                year, month, day = int(citation.getPublishingDateYear()), int(citation.getPublishingDateMonth()), int(citation.getPublishingDateDay())

                if not year:
                    LabeledWidgets.getWidgetByID(PBLDF).setContent(0)
                else:
                    if not day:
                        if not month:
                            LabeledWidgets.getWidgetByID(PBLDF).setContent(1)
                        else:
                            LabeledWidgets.getWidgetByID(PBLDF).setContent(2)
                    else: 
                        LabeledWidgets.getWidgetByID(PBLDF).setContent(3)

                LabeledWidgets.getWidgetByID(PBLDT).setContent(citation.getPublishingDate())






