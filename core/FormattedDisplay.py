from Config import *
from PyQt5 import QtCore, QtWidgets, QtGui

import CitationManagement
import LabeledWidgets

class FormattedDisplay(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent=parent)
        self.output = None
        widgetLayout = QtWidgets.QVBoxLayout()
        self.textBrowser = QtWidgets.QTextBrowser()

        self.citationFormatOutputType = LabeledWidgets.LabeledComboBox(CITEF, "Citation Format:", [CITATION_FORMAT_TYPE_MLA, CITATION_FORMAT_TYPE_APA, CITATION_FORMAT_TYPE_IEEE], DefaultCitationFormatOutputTypeWidth)

        self.applyFilters = LabeledWidgets.LabeledWidget("CITFL","Apply Filters to Citation List:")
        self.applyFilters.setWidget(QtWidgets.QCheckBox())
        self.applyFilters.getWidget().toggled.connect(self.updateDisplay)

        self.entryOutputType = LabeledWidgets.LabeledComboBox("ENOPT", "Output Order:", ["Alphabetical","Database Order"], DefaultCitationFormatOutputTypeWidth)


        widgetLayout.addWidget(self.textBrowser)
        widgetLayout.addWidget(self.citationFormatOutputType)
        widgetLayout.addWidget(self.applyFilters)
        widgetLayout.addWidget(self.entryOutputType)

        self.setLayout(widgetLayout)

        SharedObjects[CTDSP]=self

        self.citationFormatOutputType.getWidget().currentIndexChanged.connect(self.updateDisplay)
        self.entryOutputType.getWidget().currentIndexChanged.connect(self.updateDisplay)


    def updateDisplay(self):
        if self.applyFilters.getWidget().isChecked():
            enableFilter=True
        else:
            enableFilter=False

        
        if self.entryOutputType.getIndex() == 0:
            alphabetical = True
        else:
            alphabetical = False
            

        formatIndex = self.citationFormatOutputType.getIndex()
        if formatIndex == 0:
            self.setMLAFormat(enableFilter, alphabetical)
        elif formatIndex == 1:
            self.setAPAFormat(enableFilter, alphabetical)
        elif formatIndex == 2:
            self.setIEEEFormat(enableFilter, alphabetical)

        if self.textBrowser.toPlainText() in ["\".\" ", '[1] "," 0000. ', '. (0000). ','[1] ","0000. ','[Paper presentation] (0000). .', '[1] "," 2000. ', '. 2000. ','[1] , , 2000. ','[Paper presentation] (2000). .']:
            print("PLAIN", self.textBrowser.toPlainText())
            self.textBrowser.setPlainText("")



    def setMLAFormat(self, enableFilter, alpha):
        self.textBrowser.setHtml("".join(["<p style=\"text-indent:-%dpx;margin-left: %dpx;\">"%(DefaultCitationFormatOutdentation, DefaultCitationFormatOutdentation)+i+"</p>" for i in CitationManagement.mainCiteManager.getMLAFormattedListString(filtersEnabled=enableFilter, alphabetical=alpha).split("\n")]))


    def setAPAFormat(self, enableFilter, alpha):
        self.textBrowser.setHtml("".join(["<p style=\"text-indent:-%dpx;margin-left: %dpx;\">"%(DefaultCitationFormatOutdentation, DefaultCitationFormatOutdentation)+i+"</p>" for i in CitationManagement.mainCiteManager.getAPAFormattedListString(filtersEnabled=enableFilter, alphabetical=alpha).split("\n")]))

    def setIEEEFormat(self, enableFilter, alpha):
        self.textBrowser.setHtml("".join(["<p style=\"text-indent:-%dpx;margin-left: %dpx;\">"%(DefaultCitationFormatOutdentation, DefaultCitationFormatOutdentation)+i+"</p>" for i in CitationManagement.mainCiteManager.getIEEEFormattedListString(filtersEnabled=enableFilter, alphabetical=alpha).split("\n")]))

    def setHTMLString(self, htmlStr):
        self.textBrowser.setHtml(htmlStr)
        #self.textBrowser.setHtml(CitationManagement.mainCiteManager.getMLAFormattedListString().replace("\n","<br><br>"))

