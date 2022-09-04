import sys, datetime
from Config import *
from PyQt5 import QtCore, QtWidgets, QtGui

def getWidgetByID(ID):
    return LabeledWidgetsDict[ID]

class LabeledBoxGrid(QtWidgets.QWidget):
    def __init__(self, cols=1, rows=1, parent=None):
        super().__init__(parent=parent)

        self.maxCols=cols
        self.maxRows=rows

        self.glay = QtWidgets.QGridLayout()
        self.setLayout(self.glay)


        self.vspacer = QtWidgets.QSpacerItem(0, DefaultLabelBoxHeights)
        #self.vspacer = QtWidgets.QSpacerItem(0, DefaultLabelBoxHeights-10, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)

        self.widgetDict={}

        self.widgetDict2={}

        for i in range(rows):
            for j in range(cols):
                self.widgetDict2[self.indexFromRowCol(i+1,j+1)]=[]


        #self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum)

    def redrawBox(self):
        for i in self.widgetDict.keys():
            self.glay.removeWidget(i)

        for i in range(self.maxRows):
            self.glay.addItem(self.vspacer, i+1, self.maxCols+1)

        for i in self.widgetDict.keys():
            x=self.widgetDict[i][1]
            y=self.widgetDict[i][0]

            self.glay.addWidget(i,y,x)
            
    def indexFromRowCol(self, row, col):
        return "%d,%d"%(row,col)

    def rowColFromIndex(self, index):
        # Returns a list [row, col]
        return [int(i) for i in index.split(",")]

    def getCurrentShownWidgetInSlot(self, row, col):
        return self.widgetDict2[self.indexFromRowCol(row,col)][0]

    def getAllWidgetsInSlot(self, row, col):
        return self.widgetDict2[self.indexFromRowCol(row,col)]

    def swapWidgetShowInSlot(self, row, col):
        l=self.widgetDict2[self.indexFromRowCol(row,col)]
        l[0].hide()
        l.append(l.pop(0))
        l[0].show()

    def addWidget(self, row, col, widget):
        self.widgetDict[widget]=(row,col)
        self.widgetDict2[self.indexFromRowCol(row, col)].append(widget)

        if len(self.widgetDict2[self.indexFromRowCol(row, col)])>1:
            widget.hide()

        self.redrawBox()
    
    def removeWidget(self, widget):
        self.glay.removeWidget(widget)
        removedWidget=self.widgetDict.pop(widget)
        for i in self.widgetDict2.keys():
            if removedWidget in self.widgetDict2[i]:
                self.widgetDict2[i].pop(self.widgetDict2.index(removedWidget))
                if self.widgetDict2[i]:
                    self.widgetDict2[i][0].show()


        self.redrawBox()
        return removedWidget


class LabeledWidget(QtWidgets.QWidget):
    def __init__(self, ID, labelText="Label Text: ", fixedLabelWidth=None, fixedWidgetWidth=None, parent=None):
        super().__init__(parent=parent)
        self.output = None

        self.setFixedHeight(DefaultLabelBoxHeights)

        self.ID = ID
        self.checkBox = QtWidgets.QCheckBox()
        self.checkBox.setChecked(True)
        self.checkBox.hide()
        #self.checkBox.setCheckable(True)
        self.checkBox.clicked.connect(self.checkToggle)
        self.checkBox.setFixedWidth(30)
        #self.checkBox.setFixedHeight(30)

        self.hlayout = QtWidgets.QHBoxLayout()

        self.labelTextString = labelText

        self.label = QtWidgets.QLabel(labelText)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)


        if fixedLabelWidth:
            self.setLabelWidth(fixedLabelWidth)


        self.widget = QtWidgets.QWidget()

        LabeledWidgetsDict[self.ID] = self


        if fixedWidgetWidth:
            self.fixedWidgetWidth=fixedWidgetWidth
        else:
            self.fixedWidgetWidth=None
            
        self.hlayout.addWidget(self.checkBox)
        self.hlayout.addWidget(self.label)
        self.hlayout.addWidget(self.widget)
        self.setLayout(self.hlayout)

        self.__warning = False
        self.__important = False
        self.__note = False


    def setWidget(self, widget):
        self.hlayout.removeWidget(self.widget)

        self.widget = widget

        if self.fixedWidgetWidth:
            self.setFixedWidth(self.fixedWidgetWidth)

            
        self.hlayout.addWidget(self.widget)

    def getWidget(self):
        return self.widget

    def getID(self):
        return self.ID

    def setLabelWidth(self, width):
        self.label.setFixedWidth(width)
    
    def setLabelText(self, labelText=None):
        if labelText is None:
            labelText=self.labelTextString
        self.labelTextString = labelText
        self.label.setText(self.__labelTextFormat(labelText))

    def getLabelText(self):
        return self.label.text()

    def __labelTextFormat(self, text):
        newStr = text

        if self.__note:
            newStr = "<b>*</b> " + newStr

        if self.__important:
            newStr = "<b>" + newStr + "</b>"
            
        if self.__warning:
            newStr = f"<font color={WARNING_COLOR}><h3>" + newStr + "</h3></font>"


        return newStr

    def setWarningOn(self, warningOn=True):
        self.__warning = warningOn
        self.setLabelText()

    def setWarningOff(self, warningOff=True):
        self.setWarningOn(not warningOff)

    def isWarningOn(self):
        return self.__warning

    def isWarningOff(self):
        return not self.__warning

    def setNoteOn(self, noteOn=True):
        self.__note = noteOn
        self.setLabelText()

    def setNoteOff(self, noteOff=True):
        self.setNoteOn(not noteOff)

    def isNoteOn(self):
        return self.__note

    def isNoteOff(self):
        return not self.__note


    def setImportantOn(self, importantOn=True):
        self.__important = importantOn
        self.setLabelText()

    def setImportantOff(self, importantOff=True):
        self.setImportantOn(not importantOff)

    def isImportantOn(self):
        return self.__important

    def isImportantOff(self):
        return not self.__important


    def setWidgetWidth(self, width):
        self.widget.setFixedWidth(width)

    def enableCheckBox(self):
        self.checkBox.show()

    def disableCheckBox(self):
        self.checkBox.hide()

    def isCheckBoxChecked(self):
        return self.checkBox.isChecked()

    def checkToggle(self, e=None):
        if e:
            self.widget.setDisabled(False)
        else:
            self.widget.setDisabled(True)

    def isWarning(self):
        return self.__warning

    def getContent(self):
        pass



class LabeledSpinBox(LabeledWidget):
    def __init__(self, ID, labelText="Spin Box: ", defaultValue=None, minimumValue=None, maximumValue=None, fixedLabelWidth=None, fixedSpinBoxWidth=None, parent=None):
        super().__init__(ID, labelText, fixedLabelWidth, fixedSpinBoxWidth, parent)

        self.defaultValue = defaultValue
        self.minimumValue = minimumValue
        self.maximumValue = maximumValue

        self.spinBox = QtWidgets.QSpinBox()


        if self.minimumValue != None:
            self.spinBox.setMinimum(self.minimumValue)

        if self.maximumValue != None:
            self.spinBox.setMaximum(self.maximumValue)

        if self.defaultValue != None:
            self.spinBox.setValue(self.defaultValue)
        else:
            self.spinBox.setValue(0)


        self.setWidget(self.spinBox)

        self.getSpinBox = self.getWidget
        self.setContent = self.setValueOfSpinBox
        self.setSpinBoxWidth = self.setWidgetWidth
        
        if fixedSpinBoxWidth:
            self.setSpinBoxWidth(fixedSpinBoxWidth)


        '''
        self.spinBoxtextChanged(const QString &text)
        self.spinBox.valueChanged(int i)
        '''

    def getValueOfSpinBox(self):
        return self.spinBox.value()

    def setValueOfSpinBox(self, value):
        self.spinBox.setValue(int(value))

    def getContent(self):
        return self.getValueOfSpinBox()




class LabeledCalendarWidget(LabeledWidget):
    def __init__(self, ID, labelText="Calendar: ", defaultDateFormat=None, fixedLabelWidth=None, fixedCalendarWidth=None, parent=None):
        super().__init__(ID, labelText, fixedLabelWidth, fixedCalendarWidth, parent)

        self.formats = ["MMM d, yyyy",
                        "MMMM d, yyyy",
                        "MM/dd/yyyy",
                        "MM/dd/yy",
                        "M/d/yy",
                        "yyyy/MM/dd",
                        "yyyy/M/d",
                        "yyyy, MMM d",
                        "yyyy, MMMM d",
                        "MM-dd-yyyy",
                        "MM-dd-yy",
                        "M-d-yy",
                        "yyyy-MM-dd",
                        "yyyy-M-d"]


        self.calendar = QtWidgets.QDateEdit()

        self.calendar.setDate(datetime.date.today())
        self.calendar.setMaximumDate(datetime.date.today())
        self.calendar.setCalendarPopup(True)


        if defaultDateFormat is not None:
            self.setDateFormatMode(defaultDateFormat)
        else:
            self.setDateFormatMode(DefaultDateFormat)


        self.setWidget(self.calendar)

        self.getCalendar = self.getWidget
        self.setCalendarWidth = self.setWidgetWidth
        
        if fixedCalendarWidth:
            self.setCalendarWidth(fixedWidth)

    def setDateFormatMode(self, dateFormatMode=0):
        assert(0 <= dateFormatMode < len(self.formats))
        self.calendar.setDisplayFormat(self.formats[dateFormatMode])

    def getContent(self):
        cal = self.calendar.dateTime().toString("MM/dd/yyyy")
        return cal

    def setContent(self, dateStr):
        if dateStr == "":
            self.calendar.setDateTime(datetime.datetime().today())
        else:
            dateStr = [int(i) for i in dateStr.split('/')]
            if dateStr[0] == 0:
                mon = datetime.datetime.today().month
                dateStr[0]=mon
                
            if dateStr[1] == 0:
                day = datetime.datetime.today().day
                dateStr[1]=day

            if dateStr[2] == 0:
                year = datetime.datetime.today().year
                dateStr[2]=year


            self.calendar.setDateTime(datetime.datetime(dateStr[2],dateStr[0],dateStr[1]))

        
        


class LabeledComboBox(LabeledWidget):
    def __init__(self, ID, labelText="Combo Box: ", comboChoiceList=[], fixedLabelWidth=None, fixedComboBoxWidth=None, parent=None):
        super().__init__(ID, labelText, fixedLabelWidth, fixedComboBoxWidth, parent)


        self.comboBox = QtWidgets.QComboBox()

        for i in comboChoiceList:
            self.comboBox.addItem(i)


        self.setWidget(self.comboBox)

        self.getComboBox = self.getWidget
        self.setComboBoxWidth = self.setWidgetWidth
        
        if fixedComboBoxWidth:
            self.setComboBoxWidth(fixedComboBoxWidth)

        #self.comboBox.currentIndexChanged.connect(self.printComboID)


        '''
        self.comboBox.activated 
        self.comboBox.currentIndexChanged 
        self.comboBox.currentTextChanged 
        self.comboBox.editTextChanged 
        self.comboBox.highlighted 
        self.comboBox.textActivated 
        self.comboBox.textHighlighted 
        '''

    def printComboID(self, e=None):
        print(str(e),self.comboBox.currentText(), self.comboBox.currentIndex())

    def getContent(self):
        return self.comboBox.currentText()

    def getIndex(self):
        return self.comboBox.currentIndex()

    def setContent(self, index):
        self.comboBox.setCurrentIndex(int(index))

class LabeledTextBox(LabeledWidget):
    def __init__(self, ID, labelText="Text Goes Here", fixedLabelWidth=None, fixedTextInputWidth=None, maxLengthOfInput=None, parent=None):
        super().__init__(ID, labelText, fixedLabelWidth, fixedTextInputWidth, parent)
        self.textInput = QtWidgets.QLineEdit()
        self.setWidget(self.textInput)

        self.getTextBox = self.getWidget
        
        self.setTextInputWidth = self.setWidgetWidth
        self.maximumLengthOfInput = maxLengthOfInput
        
        if fixedTextInputWidth:
            self.setTextInputWidth(fixedTextInputWidth)


        if self.maximumLengthOfInput:
            self.textInput.setMaxLength(self.maximumLengthOfInput)

        self.setContent = self.setText


        '''
        self.textInput.textChanged.connect(lambda: print(self.textInput.text()))

        SIGNALS:
        cursorPositionChanged(int oldPos, int newPos)
        editingFinished()
        inputRejected()
        returnPressed()
        selectionChanged()
        textChanged(const QString &text)
        textEdited(const QString &text)
        '''

    def getText(self):
        return self.textInput.text()

    def setText(self, newText):
        self.textInput.setText(newText)

    def setMaxLengthOfInput(self, maxLengthOfInput):
        self.maximumLengthOfInput = maxLengthOfInput
        self.textInput.setMaxLength(maximumLengthOfInput)

    def getMaxLengthOfInput(self):
        return self.maximumLengthOfInput

    def getContent(self):
        return self.getText()
        


class AuthorTable(QtWidgets.QWidget):
    def __init__(self, ID, numberOfAuthors=1, parent=None):
        assert(parent != None, "")
        super().__init__(parent=parent)

        self.authorDictionary={i:['','',''] for i in range(numberOfAuthors)}

        self.setMinimumHeight(200)
        self.numberOfAuthors = numberOfAuthors

        self.nextWidgetInTabSequence = self
        self.lastWidgetInTabSequence = self

        self.tableLable = QtWidgets.QLabel("Author:")
        #self.tableLable.setFixedWidth(540)
        self.tableAuthorCount = LabeledSpinBox(NOAUT, "Author Count:", numberOfAuthors, 1, 24, DefaultLabelWidthColB,None,parent)
        self.tableAuthorCount.getSpinBox().valueChanged.connect(self.setNumberOfAuthors)

        self.headerLayout = QtWidgets.QHBoxLayout()
        self.headerLayout.addWidget(self.tableLable)
        self.headerLayout.addWidget(self.tableAuthorCount)


        self.table = QtWidgets.QTableWidget()


        self.vlay = QtWidgets.QVBoxLayout()
        #self.vlay.addWidget(self.tableLable)
        self.vlay.addLayout(self.headerLayout)
        self.vlay.addWidget(self.table)

        self.setLayout(self.vlay)

        self.table.setColumnCount(3)
        self.table.setRowCount(self.numberOfAuthors)

        self.lastCell = None

        self.setNumberOfAuthors(self.numberOfAuthors)

        self.table.setHorizontalHeaderLabels(["Last Name","First Name","Middle Initial"])
        self.table.resizeColumnsToContents()



        self.table.currentCellChanged.connect(self.onCellChange)
        self.table.cellPressed.connect(self.onCellChange)

        self.getContent = self.getAuthorDictionary
        self.setContent = self.setAuthorsByDictionary

        self.ID = ID
        LabeledWidgetsDict[self.ID] = self

 
    def getID(self):
        return self.ID

   
    def focusOutEvent(self, evt=None):
        print("Focus Out!!")
        self.table.commitData(self.table)
        self.table.setCurrentCell(0,0)
        self.cleanFieldData()


    def getTable(self):
        return self.table

    def getAuthorDictionary(self):
        # A dictionary of dictionaries
        d = {}

        c=0
        for i in range( self.numberOfAuthors ):
            row=self.getRowAsList(i)
            if row != ['','','']:
                d[c]={}
                d[c][LNAME]=row[0]
                d[c][FNAME]=row[1]
                d[c][MINIT]=row[2]
                c+=1

        if d == {}:
            print("WARNING: Author Dictionary is Empty!")
            d[0]={}
            d[0][LNAME]=""
            d[0][FNAME]=""
            d[0][MINIT]=""

        return d

    def getAuthorDictKeys(self):
        return [i for i in self.authorDictionary.keys()]

    def getRowAsList(self, row):
        assert(row < self.numberOfAuthors)
        t=[]

        for i in range(3):
            if self.table.item(row,i):
                t.append(self.table.item(row, i).text())
            else:
                t.append("")

        return t


    def clearTable(self):
        for i in range(self.numberOfAuthors):
            self.setRowByList(i, ['', '', ''])

    def refillTable(self):
        for i in range(self.numberOfAuthors):
            self.setRowByList(i, self.authorDictionary[i])


    def setRowByList(self, row, nameList):
        assert(row < self.numberOfAuthors)
        assert(len(nameList)==3)

        for i in range(3):
            if self.table.item(row,i):
                self.table.item(row,i).setText(nameList[i])

        self.authorDictionary[row]=nameList


    def onCellChange(self, cell):
        #print("OCC - FOCUS ITEM:", self.parent().focusWidget())
        #print("OCC - EDITOR:",self.table.isPersistentEditorOpen(self.table.currentItem()))
        self.cleanFieldData()
        if self.lastCell:
            if self.table.currentRow() != self.lastCell[1]:
                self.moveBlankRowsToEnd(0)


        if cell:
            self.lastCell = [self.table.currentItem(), 
                             self.table.currentRow(),
                             self.table.currentColumn()]

    
    def cleanFieldData(self):
        for i in range(self.numberOfAuthors):
            l=self.getRowAsList(i)
            l[0] = "".join([i for i in l[0] if i in AcceptableNameChars])
            l[1] = "".join([i for i in l[1] if i in AcceptableNameChars])
            l[2] = "".join([i for i in l[2] if i in AcceptableNameChars])

            if l[0]:
                l[0]=l[0][0].upper()+l[0][1::]

            if l[1]:
                l[1]=l[1][0].upper()+l[1][1::]

            if l[2]:
                l[2]=l[2][0].upper()

            self.setRowByList(i,l)

    def isRowEmpty(self, row):
        assert(0 <= row < self.numberOfAuthors)

        result=[self.table.item(row,i).text() for i in range(3)]

        return result==['','','']
        
    def isCurrentRowEmpty(self):
        return self.isRowEmpty(self.table.currentRow())

    def moveBlankRowsToEnd(self, sortAlphabetically=False):
        table = self.table

        rows = []

        for i in range(self.numberOfAuthors):
            rows.append(self.getRowAsList(i))

        if sortAlphabetically:
            # Alphabetical, middle name, first name, then last name.
            rows.sort(key=lambda x:x[2].upper())
            rows.sort(key=lambda x:x[1].upper())
            rows.sort(key=lambda x:x[0].upper())

            # Blank names are placed at end. If two people named Smith work on a project,
            # and one doesn't have a first name listed, this person will be tagged to the end.

            # "Cher" with only a first name, would appear after "Ziggy Zaggler"
            #rows.sort(key=lambda x:x[2].upper()=="")
            rows.sort(key=lambda x:x[1].upper()=="")
            rows.sort(key=lambda x:x[0].upper()=="")

        # Put the empty rows at the end
        rows.sort(key=lambda x:x==['','',''])

        # Set the contents of each row in the table based on the sorted rows.
        for i in range(self.numberOfAuthors):
            self.setRowByList(i,rows[i])

    def setAuthorsByDictionary(self, authorDict):
        #self.setNumberOfAuthors(len(authorDict))
        #print("AUTH DICT INPUT:", authorDict)
        self.tableAuthorCount.setValueOfSpinBox(len(authorDict))

        newDict = {}
        for i in authorDict:
            newDict[i] = [authorDict[i][j] for j in [LNAME, FNAME, MINIT]]

        self.authorDictionary = newDict
        #print("AUTH DICT:", self.authorDictionary)
        
        for i,j in enumerate(self.authorDictionary):
            #print("AUTH DICT ENUM:",i,j,self.authorDictionary[j])
            self.setRowByList(i, self.authorDictionary[j])
            #self.setRowByList(i,[authorDict[j][k] for k in [LNAME, FNAME, MINIT]])

    def setNumberOfAuthors(self, numberOfAuthors):
        assert(numberOfAuthors >= 0)
        self.numberOfAuthors = int(numberOfAuthors);
        
        self.table.setRowCount(self.numberOfAuthors)

        self.table.clearContents()
        
        if numberOfAuthors > 1:
            self.tableLable.setText("Authors:")
        else:
            self.tableLable.setText("Author:")


        for row in range(self.numberOfAuthors):
            for col in range(3):
                self.table.setItem(row, col, QtWidgets.QTableWidgetItem(""))


        for i in range(self.numberOfAuthors):
            if i in self.authorDictionary.keys():
                self.setRowByList(i,self.authorDictionary[i])
            else:
                self.setRowByList(i, ['','',''])




    def getNumberOfAuthors(self):
        return self.numberOfAuthors

    def resizeEvent(self,e=None):
        #print("Resized!")
        self.table.setCurrentCell(0,0)

    def deleteTextInCurrentCell(self):
        for i in self.table.selectedItems():
            i.setText("")

        row=self.table.currentRow()
        col=self.table.currentColumn()

        self.table.clearSelection()
        self.table.setCurrentCell(row, col)


    def enterTextInCurrentCell(self):
        if self.table==self.parent().focusWidget():
            #if self.table.currentItem().text() != "":
            if not self.isCurrentRowEmpty():
                row = self.table.currentRow()+1
                self.table.clearSelection()
                if row < self.table.rowCount():
                    self.table.setCurrentCell(row, 0)
                else:
                    self.table.setCurrentCell(0, 0)
            else:
                self.table.editItem(self.table.currentItem())


    def tabLastCelltoNextChildWidget(self): 
        if self.table==self.parent().focusWidget():
            #print("TB:",self.table.currentRow(), self.table.currentColumn())

            if (self.table.currentRow() == self.numberOfAuthors-1 and self.table.currentColumn() == 2) or self.isCurrentRowEmpty():
                self.table.clearSelection()
                self.table.setCurrentCell(0,0)
                self.table.editItem(self.table.currentItem())
                self.nextWidgetInTabSequence.setFocus()
            
            else:
                if self.table.currentColumn()<2:# and self.table.currentItem().text() != "":
                    col=self.table.currentColumn() + 1
                    row=self.table.currentRow()
                else:
                    col=0
                    row=self.table.currentRow() + 1

                self.table.clearSelection()
                self.table.setCurrentCell(row%self.numberOfAuthors, col)

    def backtabLastCelltoNextChildWidget(self):
        if self.table==self.parent().focusWidget():
            if self.table.currentRow() == 0 and self.table.currentColumn() == 0:
                self.lastWidgetInTabSequence.setFocus()
                self.table.clearSelection()
                self.table.setCurrentCell(0,0)
            else:
                if self.table.currentColumn() != 0:
                    col=self.table.currentColumn() - 1
                    row=self.table.currentRow()
                else:
                    col=2
                    row=self.table.currentRow() - 1

                self.table.setCurrentCell(row%self.numberOfAuthors, col)

    def setNextWidgetInTabSequence(self, widget):
        self.nextWidgetInTabSequence = widget

    def setLastWidgetInTabSequence(self, widget):
        self.lastWidgetInTabSequence = widget


    def resizeColumnsProportionally(self,e=None):
        proportionOfNames = .40
        
        # Resize the LastName and FirstName columns to the same proportion of width
        self.table.setColumnWidth(0, int(self.width()*proportionOfNames))
        self.table.setColumnWidth(1, int(self.width()*proportionOfNames))
        
        # Resize middle initial column to be smaller and stretch fill to end.
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)


