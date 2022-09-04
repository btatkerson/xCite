import datetime

from Config import *

def generateEmptyCitationDictionary():
    emptyDict = {TYPE  : DefaultTypeOfContent,  
                 TITLE : "", 
                 AUTHT : {0:{LNAME : "", FNAME : "", MINIT : ""}},
                 VOLUM : "", 
                 ISSUE : "", 
                 PAGES : "", 
                 PBLCA : "", 
                 PBLSH : "", 
                 PBLDT : DefaultDate, 
                 PBLYR : "", 
                 PBCTY : "", 
                 ACCDT : DefaultDate, 
                 URL   : ""}

    return emptyDict

###################################################################################
#               Citation Class
###################################################################################

class CitationManager():
    def __init__(self):
        self.output = None
        self.citationIDCount = -1
        self.citations = []
        self.headers = []
        self.permanentCitationDict = {}
        self.removedCitations = {}

        self.currentFile = None

        self.appliedFilters = {TYPEF : None,  
                               FILTI : None,
                               FILLN : None,
                               FILFN : None,
                               FILMI : None,
                               EXCTF : None}

        self.filtersEnabled=False

    def setFiltersEnabled(self, enabled=True):
        self.filtersEnabled = enabled

    def getFiltersEnabled(self):
        return self.filtersEnabled

    def setFilter(self, ftype, value):
        assert ftype in self.appliedFilters, "Not a valid filter type"
        self.appliedFilters[ftype] = value

    def getFilter(self, ftype):
        assert ftype in self.appliedFilters, "Not a valid filter type"
        return self.appliedFilters[ftype]


    def setOutput(self, output):
        self.output = output
        for i in self.permanentCitationDict:
            self.permanentCitationDict[i].output=output

    def readInDatabaseFromFile(self, file=None, newfile=False, template=False):
        '''
        Reads all the contents from the database file and stores them into instances of
        the citation class.
        '''
        self.citationIDCount = -1
        self.citations = []
        self.headers = []
        self.permanentCitationDict = {}
        self.removedCitations = {}


        if file is None:
            file = DefaultFileInput
        print("FILE readin:",file)

        if newfile == True:
            f=open(DefaultCleanFile, 'r')
            contents = f.read()
            f.close()
        elif template == True:
            f=open(DefaultTemplateFile, 'r')
            contents = f.read()
            f.close()
        else:
            f=open(file, 'r')
            contents = f.read()
            f.close()
            self.currentFile=file

        contents = contents.split('\n')
        contents = [i.split('\t') for i in contents]
        self.headers = contents.pop(0)
        print(contents)


        citation = None
        currentRecordEmpty = False
        firstRecord = True
        
        for i in contents:
            # if type and title are given
            if ''.join(i[0:2]) != '':
                #print(i[0::])
                if not currentRecordEmpty:
                    citation = self.newCitation()
                else:
                    currentRecordEmpty = False



                citation.setTypeOfContent(i[0])

                if i[1] == "" and firstRecord:
                    pass
                else:
                    citation.setTitle(i[1])
                citation.addAuthor(i[2], i[3], i[4])
                citation.setVolume(i[5])
                citation.setIssue(i[6])
                citation.setPages(i[7])
                citation.setPublication(i[8])
                citation.setPublisher(i[9])

                # If a publishedYear is given (book)
                if i[10]:
                    try:
                        citation.setPublishedYear(i[10])
                    except AssertionError:
                        citation.clearCitationInformation()
                        print("Publishing year (%s) outside of Valid Date Range"%(i[10]))
                        print("Ignoring record")
                        currentRecordEmpty=True

                # If a publishedDate is given (article, con paper)
                if i[11]:
                    try:
                        citation.setPublishingDateByString(i[11])
                    except AssertionError:
                        citation.clearCitationInformation()
                        print("Publishing date (%s) outside of Valid Date Range"%(i[11]))
                        print("Ignoring record")
                        currentRecordEmpty=True

                # Only happens when a record has faulty data and gets ignored
                if not currentRecordEmpty:
                    citation.setPublishingCity(i[12].title(),1)
                    if i[13]:
                        citation.setAccessDateByString(i[13])
                    citation.setURL(i[14])

            # If the first two fields (type, title) are empty, add another author
            # to the previous entry
            else:
                if ''.join(i[2:5]) != '':
                    citation.addAuthor(i[2], i[3], i[4])
            firstRecord = False


    def writeCitationsToDatabase(self, file=None):
        if file == None:
            file = DefaultFileOutput
        contentToWrite = "\t".join(self.headers)+"\n"

        nonRemovedCitations = self.getCurrentDictOfCitations()

        for i in nonRemovedCitations:
            #print("NRC:",i,nonRemovedCitations[i].isCitationSet())
            if nonRemovedCitations[i].isCitationSet():
                contentToWrite += self.permanentCitationDict[i].getCitationStringForDB()

        f = open(file,"w")
        f.write(contentToWrite)
        f.close()

        self.output("Database has been saved to:<br>%s"%(file),append=True)

    def containsOneValidRecord(self):
        for i in self.permanentCitationDict:
            if self.permanentCitationDict[i].isCitationSet():
                return True
        return False


    def __pullNewID(self):
        # Used for storing citations in dict with unique keys
        self.citationIDCount += 1
        return self.citationIDCount 

    def addCitation(self, citation):
        assert isinstance(citation, Citation), "Citation must be given to addCitation!"
        if citation not in self.citations:
            print('%s added to the citation dictionary.'%(citation))
            self.citations.append(citation)
            self.permanentCitationDict[self.__pullNewID()]=citation

    def newCitation(self):
        newCit = None

        for i in self.permanentCitationDict:
            if not self.permanentCitationDict[i].isCitationSet():
                if i not in self.removedCitations:
                    newCit = self.permanentCitationDict[i]
                    #self.restoreCitationByID(i)
                    break

        if not newCit:
            newCit = Citation()
            self.addCitation(newCit)


        newCit.output = self.output
        return newCit

    def removeCitationByID(self, ID):
        self.removeCitation(self.getCitationByID(ID))


    def removeCitation(self, citation):
        assert isinstance(citation, Citation), "Citation must be given to addCitation!"
        if citation in self.citations and len(self.citations) > 1:
            indexOfCitation = self.citations.index(citation)
            self.citations.pop(indexOfCitation)
            citation.citationIsSet = False
            self.removedCitations[self.getIDByCitation(citation)] = citation

    def restoreCitationByID(self, ID):
        self.restoreCitation(self.getCitationByID(ID))

    def restoreCitation(self, citation):
        if citation in self.permanentCitationDict.values():
            if self.getIDByCitation(citation) in self.removedCitations:
                citation.citationIsSet = True
                self.removedCitations.pop(self.getIDByCitation(citation))
                self.resetCurrentCitationList()
                return True
        return False

    def resetCurrentCitationList(self):
        # Resets the citation list to only show non-removed citations.
        
        newCitationList = []
        for i in sorted(self.permanentCitationDict.keys()):
            if i not in self.removedCitations:
                newCitationList.append(self.permanentCitationDict[i])
        self.citations = newCitationList

    def getNonRemovedCitations(self):
        nonrem = []
        for i in self.permanentCitationDict:
            if i not in self.removedCitations:
                nonrem.append(i)

        d = {}
        for i in nonrem:
            d[i]=self.permanentCitationDict[i]
        return d


    def getIDByCitation(self, citation):
        if citation in self.permanentCitationDict.values():
            for i in self.permanentCitationDict:
                if self.permanentCitationDict[i] == citation:
                    return i
        return -1

    def getCitationByID(self, ID):
        if ID in self.permanentCitationDict:
            return self.permanentCitationDict[ID]

        return None


    def getNumberOfCitations(self):
        return len(self.citations)

    def getPermanentDictOfCitations(self):
        '''
        Returns a dict of all citations in the application since loading the database
        Format of returned dict: {ID: Citation}
        '''
        tempDict = {}
        for i in self.permanentCitationDict:
            tempDict[i]=self.permanentCitationDict[i]

        return tempDict

    def getCurrentDictOfCitations(self):
        '''
        Returns a dict in format {ID: Citation} for all the non-removed items
        '''
        tempDict = {}
        for i in self.permanentCitationDict:
            if i not in self.removedCitations:
                tempDict[i]=self.permanentCitationDict[i]

        return tempDict

    def getCurrentDictOfFilteredCitations(self,overrideEnable=False):
        tempDict = self.getCurrentDictOfCitations()

        if not self.filtersEnabled and not overrideEnable:
            return tempDict

        ctype = self.getFilter(TYPEF)
        title = self.getFilter(FILTI)
        lastname = self.getFilter(FILLN)
        firstname = self.getFilter(FILFN)
        middleinit = self.getFilter(FILMI)
        exact = self.getFilter(EXCTF)


        if ctype:
            if ctype == 1:
                tempDict = self.getAllArticles()
            elif ctype == 2:
                tempDict = self.getAllBooks()
            elif ctype == 3:
                tempDict = self.getAllConferencePapers()


        foundRecords = {i: tempDict[i] for i in tempDict}

        if title:
            keys=[]
            for i in foundRecords:
                if foundRecords[i].isTitleInCitation(title, exact):
                    keys.append(i)
            foundRecords = {i:foundRecords[i] for i in keys}

        # If a name filter is applied
        if lastname+middleinit+firstname:
            keys=[]
            for i in foundRecords:
                if foundRecords[i].isAuthorInCitation(lastname, firstname, middleinit, exact):
                    keys.append(i)

            foundRecords = {i:foundRecords[i] for i in keys}

        return foundRecords





    def getCitationByID(self, ID):
        assert(ID in self.permanentCitationDict)
        return self.permanentCitationDict[ID]

    def getAllArticles(self):
        curDic = self.getCurrentDictOfCitations()
        return {i:curDic[i] for i in curDic if curDic[i].getTypeOfContent() == TYPE_ARTICLE}
        #return [i for i in self.citations if i.getTypeOfContent() == TYPE_ARTICLE]

    def getAllBooks(self):
        curDic = self.getCurrentDictOfCitations()
        return {i:curDic[i] for i in curDic if curDic[i].getTypeOfContent() == TYPE_BOOK}
        #return [i for i in self.citations if i.getTypeOfContent() == TYPE_BOOK]

    def getAllConferencePapers(self):
        curDic = self.getCurrentDictOfCitations()
        return {i:curDic[i] for i in curDic if curDic[i].getTypeOfContent() == TYPE_CONFERENCE_PAPER}
        #return [i for i in self.citations if i.getTypeOfContent() == TYPE_CONFERENCE_PAPER]

    def __getAlphaNumeric(self, string):
        newStr = ""

        detagged=""

        inTag = False

        for i in string:
            if i == "<":
                inTag = True

            if not inTag:
                detagged+=i

            if i == ">":
                inTag = False

        for i in detagged:
            if i.isalnum():
                newStr+=i
        return newStr

    def getMLAFormattedListString(self, citationList=None, filtersEnabled=False, alphabetical=True):

        listString = []

        if citationList:
            citations = [i.getMLAFormat() for i in citationList]
        else:
            if filtersEnabled:
                currentCitations = self.getCurrentDictOfFilteredCitations()
            else:
                currentCitations = self.getCurrentDictOfCitations()
            citations = [currentCitations[i].getMLAFormat() for i in currentCitations]

        # Sort MLA Citations alphabetically
        if alphabetical:
            for i in sorted(citations, key=lambda x: self.__getAlphaNumeric(x)):
                listString.append(i)
        else:
            for i in citations:
                listString.append(i)
        return "\n".join(listString)


    def getAPAFormattedListString(self, citationList=None, filtersEnabled=False, alphabetical=True):

        listString = []

        if citationList:
            citations = [i.getAPAFormat() for i in citationList]
        else:
            if filtersEnabled:
                currentCitations = self.getCurrentDictOfFilteredCitations()
            else:
                currentCitations = self.getCurrentDictOfCitations()
            citations = [currentCitations[i].getAPAFormat() for i in currentCitations]

        # Sort APA Citations alphabetically
        if alphabetical:
            for i in sorted(citations, key=lambda x: self.__getAlphaNumeric(x)):
                listString.append(i)
        else:
            for i in citations:
                listString.append(i)
        return "\n".join(listString)




    def getIEEEFormattedListString(self, citationList=None, filtersEnabled=False, alphabetical=True):

        listString = []

        if citationList:
            citations = [i.getIEEEFormat() for i in citationList]
        else:
            if filtersEnabled:
                currentCitations = self.getCurrentDictOfFilteredCitations()
            else:
                currentCitations = self.getCurrentDictOfCitations()
            citations = [currentCitations[i].getIEEEFormat() for i in currentCitations]

        countCites = 0
        # Sort IEEE Citations alphabetically
        if alphabetical:
            for i in sorted(citations, key=lambda x: self.__getAlphaNumeric(x)):
                countCites += 1
                listString.append("[%d] %s"%(countCites,i))
        else:
            for i in citations:
                countCites += 1
                listString.append("[%d] %s"%(countCites,i))
        return "\n".join(listString)








###################################################################################
#               Citation Class
###################################################################################
class Citation():
    def __init__(self, citationDict = None, parent=None):
        self.parent = parent
        self.previousDict = None
        self.citationDict = generateEmptyCitationDictionary()

        if citationDict:
            self.setCitationInfoByDictionary(citationDict)

        self.citationIsSet=False

    def isCitationSet(self):
        return self.citationIsSet

    def setCitationInfoByDictionary(self, citationDict):
        self.setTypeOfContent(citationDict[TYPE])
        self.output("")
        failed=False

        try:
            LabeledWidgetsDict[TITLE].setWarningOff()
            LabeledWidgetsDict[TITLE].setNoteOff()
            self.setTitle(citationDict[TITLE])
        except AssertionError:
            if self.previousDict:
                self.citationDict = self.previousDict
            self.citationDict[TITLE]=None
            self.citationIsSet=False
            LabeledWidgetsDict[TITLE].setWarningOn()
            LabeledWidgetsDict[TITLE].setNoteOn()
            self.output("<font color=%s>Warning:</font> Title <i>must</i> be set. Record not added to citations.<br>" % (WARNING_COLOR)) 
            failed=True


        try:
            self.setPublishingCity(citationDict[PBCTY])
            LabeledWidgetsDict[PBCTY].setNoteOff()
        except AssertionError:
            if "," in citationDict[PBCTY]:
                citationDict[PBCTY]=citationDict[PBCTY][0:citationDict[PBCTY].index(",")]

            cleanCity=""
            cleanSpaceStr = " ".join(citationDict[PBCTY].split(",")).replace("  "," ")


            while cleanSpaceStr.endswith(' '):
                cleanSpaceStr = cleanSpaceStr[0:-1]
                
            for i in cleanSpaceStr:
                if i in AcceptableNameChars:
                    cleanCity+=str(i)

            self.output("<b><font color=%s>*Note:</font></b> Publishing City (%s) should be in format \"City, State Abbr\"<br>" % (YIELD_COLOR,cleanCity.title()),append=True)

            LabeledWidgetsDict[PBCTY].setNoteOn()
            self.citationDict[PBCTY]=cleanCity.title()

        self.setAuthors(citationDict[AUTHT])
        self.setVolume(citationDict[VOLUM])
        self.setIssue(citationDict[ISSUE])
        self.setPages(citationDict[PAGES])
        self.setPublication(citationDict[PBLCA])
        self.setPublisher(citationDict[PBLSH])
        self.setPublishedYear(citationDict[PBLYR])
        self.setPublishingDateByString(citationDict[PBLDT])


        self.setAccessDateByString(citationDict[ACCDT])
        self.setURL(citationDict[URL])

        if failed:
            return

        self.citationIsSet = True

        #if self.previousDict:
        #    if self.previousDict != self.citationDict:
        #self.output("Changes made to record: %s"%(self.getTitle()),append=True)
        self.previousDict = {i:self.citationDict[i] for i in self.citationDict}

    def getCitationStringForDB(self):
        citationPropertyList = []

        citationPropertyList.append(self.getTypeOfContent())
        citationPropertyList.append(self.getTitle())
        citationPropertyList.append(self.getAuthorLastNameByIndex(0))
        citationPropertyList.append(self.getAuthorFirstNameByIndex(0))
        citationPropertyList.append(self.getAuthorMiddleInitialByIndex(0))
        citationPropertyList.append(self.getVolume())
        citationPropertyList.append(self.getIssue())
        citationPropertyList.append(self.getPages())
        citationPropertyList.append(self.getPublication())
        citationPropertyList.append(self.getPublisher())


        citationPropertyList.append(self.getPublishedYear())
        citationPropertyList.append(self.getPublishingDate())
        '''
        if self.getTypeOfContent() == TYPE_BOOK:
            citationPropertyList.append(self.getPublishedYear())
            citationPropertyList.append("")
        else:
            citationPropertyList.append("")
            citationPropertyList.append(self.getPublishingDate())
        '''


        citationPropertyList.append(self.getPublishingCity())
        citationPropertyList.append(self.getAccessDate())
        citationPropertyList.append(self.getURL())

        citationPropertyList = "\t".join(citationPropertyList)

        for i in range(self.getNumberOfAuthors()-1):
            newAuthor = ["\n"]

            for j in range(1):
                newAuthor.append("")

            newAuthor.append(self.getAuthorLastNameByIndex(i+1))
            newAuthor.append(self.getAuthorFirstNameByIndex(i+1))
            newAuthor.append(self.getAuthorMiddleInitialByIndex(i+1))

            for j in range(10):
                newAuthor.append("")

            citationPropertyList += "\t".join(newAuthor)

        return citationPropertyList + '\n'

  
    def clearCitationInformation(self):
        self.citationDict = generateEmptyCitationDictionary()

    def getCitationDictionary(self):
        return self.citationDict

    def getTypeOfContent(self, numeric=False):
        if numeric:
            return {i[1]:i[0] for i in CONTENT_TYPE.items()}[self.citationDict[TYPE]]
        return self.citationDict[TYPE]

    def setTypeOfContent(self, typeOfContent):
        #print(typeOfContent)
        if type(typeOfContent) == int:
            assert(typeOfContent in CONTENT_TYPE)
            self.citationDict[TYPE] = CONTENT_TYPE[typeOfContent]
        else:
            assert(typeOfContent in CONTENT_TYPE.values())
            self.citationDict[TYPE] = typeOfContent

    def getTitle(self):
        return self.citationDict[TITLE]

    def setTitle(self, title):
        assert(title != "")
        self.citationIsSet = True
        self.citationDict[TITLE] = str(title)

    def getAuthors(self):
        if self.citationDict:
            return self.citationDict[AUTHT]
        return {0: {LNAME: "", FNAME: "", MINIT: ""}}

    def addAuthor(self, lastname, firstname="", middleinit=""):
        authDict = self.citationDict[AUTHT]
        numOfAuthors = len(authDict)
        if authDict[0][LNAME]+authDict[0][FNAME]+authDict[0][MINIT] == "":
            numOfAuthors = 0
        self.citationDict[AUTHT][numOfAuthors] = {LNAME: lastname, FNAME: firstname, MINIT: middleinit}

        self.setAuthors()

    def removeAuthorByIndex(self, index):
        assert(len(self.citationDict[AUTHT]) > 1)
        assert(index in self.citationDict[AUTHT])
        self.citationDict[AUTHT].pop(index)
        self.setAuthors()

    def setAuthors(self, authors=None):
        '''
        Accepts authors in a dictionary format with ID number and dictionary of names

        ie: {0: {LNAME: "Anderson", FNAME: "Aaron", MINIT: "A"}}
            or
            {0: {LNAME: "Anderson", FNAME: "Aaron", MINIT: "A"},
             1: {LNAME: "Bouchard", FNAME: "Bobby", MINIT: "B"}}

        '''
        if authors != None:
            assert(len(authors) > 0)
            assert(False not in [[i in authors[j] for i in [LNAME, FNAME, MINIT]] for j in authors])
        else:
            authors = self.citationDict[AUTHT]

        newAuthorDict = {0:{LNAME:"", FNAME:"", MINIT:""}}

        # Rebuilds author dictionary to assure ID numbers start at zero and increment by one
        # Also makes sure the name data uses only acceptable characters
        countIndex = 0
        for j in sorted(authors):
            if authors[j][LNAME] + authors[j][FNAME] != "":
                newAuthorDict[countIndex] = {k: self.__cleanName(authors[j][k]) for k in authors[j]}
                countIndex+=1
        
        self.citationDict[AUTHT] = newAuthorDict

    def __cleanName(self, name):
        tempName=""
        for i in name:
            if i in AcceptableNameChars:
                tempName+=i
        return tempName

    def getTopAuthor(self):
        return self.citationDict[AUTHT][0]

    def getNumberOfAuthors(self):
        return len(self.citationDict[AUTHT])

    def getAuthorByIndex(self, index):
        assert(0 <= index <= self.getNumberOfAuthors())
        return self.citationDict[AUTHT][index]

    def getAuthorFirstNameByIndex(self, index=0):
        return self.getAuthorByIndex(index)[FNAME]

    def getAuthorLastNameByIndex(self, index=0):
        return self.getAuthorByIndex(index)[LNAME]

    def getAuthorMiddleInitialByIndex(self, index=0):
        return self.getAuthorByIndex(index)[MINIT]

    def isTitleInCitation(self, titleString, exactMatch = False):
        if exactMatch:
            if titleString.upper() == self.citationDict[TITLE].upper():
                return True
        else:
            if titleString.upper() in self.citationDict[TITLE].upper():
                return True
        return False


    def isAuthorInCitation(self, lastname=None, firstname=None, middleinit=None, exactMatch=False, returnAuthors=False):

        # Make sure at least one of the name fields is filled in
        assert([lastname, firstname, middleinit] != [None, None, None])

        # Create a copy of the current author dictionary
        authDict={i:{LNAME:self.citationDict[AUTHT][i][LNAME], FNAME:self.citationDict[AUTHT][i][FNAME], MINIT:self.citationDict[AUTHT][i][MINIT]} for i in self.citationDict[AUTHT]}

        authDictKeys = list(authDict.keys())
        authorsFound = False
               
        # Check each name for a match
        for nameIDSet in [[lastname, LNAME], [firstname, FNAME], [middleinit, MINIT]]:
            name = nameIDSet[0]
            ID = nameIDSet[1]

            #print("NAME-ID:", name,ID)
            
            # If lastname, firstname, or middleinit is NOT blank
            if name:
                for i in authDictKeys[::-1]:
                    if exactMatch:
                        if name.upper() != authDict[i][ID].upper():
                            authDict.pop(i)
                            authDictKeys.remove(i)
                    else:
                        if name.upper() not in authDict[i][ID].upper():
                            authDict.pop(i)
                            authDictKeys.remove(i)
                    

        if returnAuthors:
            return authDict


        if len(authDict) > 0:
            return True
        else:
            return False
        

    def getVolume(self):
        return self.citationDict[VOLUM]

    def setVolume(self, volume):
        if volume != "":
            assert(int(volume))
        self.citationDict[VOLUM] = str(volume)

    def getIssue(self):
        return self.citationDict[ISSUE]

    def setIssue(self, issue):
        if issue != "":
            assert(int(issue))
        self.citationDict[ISSUE] = str(issue)

    def getPages(self):
        return self.citationDict[PAGES]

    def setPages(self, pages): 
        pages = str(pages)
        acceptedPageChars = "0123456789,-"

        # Clear extra characters out of the page string
        pageString = "".join([i for i in pages if i in acceptedPageChars])
        pageList = pageString.split(",")
        pageList = [i.split("-") for i in pageList]

        finalPageString = ""

        usedPages = []
        for i in pageList:
            if i not in usedPages:
                usedPages.append(i)
        #print(usedPages)

        if usedPages[0][0] == "":
            self.citationDict[PAGES] = ""
            return

        usedPages = sorted(usedPages, key = lambda x: int(x[0]))
        usedPages = sorted(usedPages, key = lambda x: '-' in x[0])

        for i in usedPages:
            if len(i) == 1:
                if i[0] != "":
                    finalPageString += i[0] + ", " 
            elif len(i) > 1:
                finalPageString += i[0] + " - " + i[1] + ", " 
        
        # Remove comma and space at the end
        finalPageString = finalPageString[0:-2]

        #print("PAGES:", finalPageString)

        self.citationDict[PAGES] = finalPageString

    def getPublication(self):
        return self.citationDict[PBLCA]

    def setPublication(self, publication):
        publicationAcceptableChars = AcceptableNameChars + "."
        publication = "".join([i for i in str(publication) if i in publicationAcceptableChars])
        self.citationDict[PBLCA] = publication
        

    def getPublisher(self):
        return self.citationDict[PBLSH]

    def setPublisher(self, publisher):
        publisherAcceptableChars = AcceptableNameChars + "."
        publisher = "".join([i for i in str(publisher) if i in publisherAcceptableChars])
        self.citationDict[PBLSH] = publisher

    def getPublishingCity(self):
        return self.citationDict[PBCTY]

    def setPublishingCity(self, city, allowWOState=False):
        if city == "":
            self.citationDict[PBCTY]=""
        else:
            # Split city from state
            city = city.split(",")

            # Makes sure split is list of two items
            # will make exception for no state needed
            if not allowWOState:
                assert (len(city) == 2)

            # Make sure city only uses acceptable characters
            city[0]="".join([i for i in city[0] if i in AcceptableNameChars])

            if allowWOState and len(city) == 1:
                self.citationDict[PBCTY]="%s"%(city[0].title())
                return

                

            # Removes spaces and unnecessary characters
            city[1]="".join([i.upper() for i in city[1] if i.isalpha()])

            # State better be two letter abbreviation, friendo
            assert (len(city[1]) == 2)

            # Set publishing city to "City, ST" format
            self.citationDict[PBCTY]="%s, %s"%(city[0].title(), city[1])
            

    def getURL(self):
        return self.citationDict[URL]

    def setURL(self, newURL):
        acceptableURLChars = [i for i in AcceptableNameChars + "0123456789:/?_=" if i != " "]
        newURL = "".join([i for i in newURL if i in acceptableURLChars])
        self.citationDict[URL] = newURL

    def getPublishedYear(self):
        return self.citationDict[PBLYR]

    def setPublishedYear(self, publishedYear):
        if publishedYear not in [0,'']:
            assert(1450 <= int(publishedYear) <= datetime.date.today().year)
        self.citationDict[PBLYR] = str(publishedYear)

    def __cleanDateString(self, datestring):
        # print("CLEAN DATESTRING", datestring)
        # Get an idea if the right kind of string was given
        # 10 chars long, two slashes in index 2 and 5
        # essentially: XX/XX/XXXX
        #print("DATE STRING: ", datestring)


        if datestring != "00/00/0000":
            assert(len(datestring) == 10)
            assert(datestring[2] == "/" and datestring[5]  == "/")

            # Break the date up into [month, day, year]
            datestring = datestring.split("/")

            # date string has three components
            assert(len(datestring) == 3)

            # Dates are within proper limits
            assert(0 <= int(datestring[0]) <= 12)
            assert(0 <= int(datestring[1]) <= DATE_MONTH_MAX_DAY[int(datestring[0])])
            assert(1450 <= int(datestring[2]) <= datetime.date.today().year)
        else:
            return "00/00/0000"

        # Check that leap year isn't given on an improper year
        if int(datestring[0]) == 2 and int(datestring[1]) == 29:
            # Century leap years only happen for centuries that are
            # multiples of 400.
            if int(datestring[2]) % 100 == 0:
                assert int(datestring[2])%400 == 0, "%s is not a leap year!"%(datestring[2])
            else:
                assert int(datestring[2])%4 == 0, "%s is not a leap year!"%(datestring[2])

        return "/".join([i for i in datestring])

    def __generateDateString(self, month='00', day='00', year='00'):
        month = str(month)
        day = str(day)
        year = str(year)

        if int(month) < 10:
            month="0"+str(int(month))
        if int(day) < 10:
            day="0"+str(int(day))

        while len(year) < 4:
            year = "0" + year

        print("YMD", year, month, day)

        return self.__cleanDateString("%s/%s/%s"%(month,day,year))
 
    def getPublishingDate(self):
        return self.citationDict[PBLDT]

    def setPublishingDateByString(self, datestring):
        if datestring:
            self.citationDict[PBLDT] = self.__cleanDateString(datestring)
        else:
            self.citationDict[PBLDT] = ""

    def setPublishingDate(self, month='00', day='00', year='0000'):
        self.citationDict[PBLDT] = self.__generateDateString(month, day, year)

    def getAccessDate(self):
        return self.citationDict[ACCDT]

    def setAccessDateByString(self, datestring):
        self.citationDict[ACCDT] = self.__cleanDateString(datestring)

    def setAccessDate(self, month, day, year):
        self.citationDict[ACCDT] = self.__generateDateString(month, day, year)

    def getPublishingDateMonth(self):
        return self.getPublishingDate().split('/')[0]

    def getPublishingDateMonthAbbreviation(self):
        return DATE_MONTH_ABBREVIATION[int(self.getPublishingDate().split('/')[0])]

    def getPublishingDateMonthFull(self):
        return DATE_MONTH_FULL[int(self.getPublishingDate().split('/')[0])]

    def getPublishingDateDay(self):
        return self.getPublishingDate().split('/')[1]
    
    def getPublishingDateYear(self):
        return self.getPublishingDate().split('/')[2]

    def getAccessDateMonth(self):
        return self.getAccessDate().split('/')[0]

    def getAccessDateMonthAbbreviation(self):
        return DATE_MONTH_ABBREVIATION[int(self.getAccessDate().split('/')[0])]

    def getAccessDateMonthFull(self):
        return DATE_MONTH_FULL[int(self.getAccessDate().split('/')[0])]

    def getAccessDateDay(self):
        return self.getAccessDate().split('/')[1]
    
    def getAccessDateYear(self):
        return self.getAccessDate().split('/')[2]


    def __getMLAAuthors(self):
        '''
        Handles the string formatting of single or multiple authors
        '''
        authtable = self.citationDict[AUTHT]
        authstring = ''

        if len(authtable) == 1:
            lname = authtable[0][LNAME]
            fname = authtable[0][FNAME]
            minit = authtable[0][MINIT]

            if lname+fname+minit != "":
                if lname:
                    authstring += lname
                    if fname:
                        authstring += ', ' + fname
                        if minit:
                            authstring += ' ' + minit
                elif fname:
                    authstring += fname
                    if minit:
                        authstring += ' ' + minit

                if authstring[-1] != ".":
                    authstring += '. '
            else:
                return ""



        #elif len(authtable) <= 3:
        else:
            lname = authtable[0][LNAME]
            fname = authtable[0][FNAME]
            minit = authtable[0][MINIT]
            
            if lname:
                authstring += lname
                if fname:
                    authstring += ', ' + fname
                    if minit:
                        authstring += ' ' + minit + '.'
            elif fname:
                authstring += fname
                if minit:
                    authstring += ' ' + minit + '.'


            for i in range(1, len(authtable)):
                if i >= DefaultMLAMaxAuthors:
                    authstring += ", et al"
                    break
                if i == len(authtable)-1:
                    authstring += ' and'
                else:
                    authstring += ','

                lname = authtable[i][LNAME]
                fname = authtable[i][FNAME]
                minit = authtable[i][MINIT]

                if fname:
                    authstring += " " + fname 
                    if minit:
                        authstring += " " + minit + "."
                    if lname:
                        authstring += " " + lname 
                else:
                    authstring += " " + lname 
            authstring += ". "

        return authstring

    def __getMLAPublishingDateFormat(self):
        newDateString = ""
        
        if self.citationDict[TYPE] == TYPE_BOOK:
            newDateString = self.citationDict[PBLYR] + ". "
        else:
            day = str(int(self.getPublishingDateDay())) + " "
            month = self.getPublishingDateMonthAbbreviation() + " "
            year = self.getPublishingDateYear()
            if year != "0000":
                year += ". "
            else:
                return ""


            if month != " ":
                if day not in [" ", "0 "]:
                    newDateString += day
                newDateString += month

            newDateString += year

        return newDateString

    def __getMLAAccessDateFormat(self):
        newDateString = ""
        
        day = str(int(self.getAccessDateDay())) + " "
        month = self.getAccessDateMonthAbbreviation() + " "
        year = self.getAccessDateYear() + ". "

        if month != " ":
            if day not in [" ", "0 "]:
                newDateString += day
            newDateString += month
        newDateString += year

        return newDateString


    def __formatItalic(self, string):
        return "<i>" + string + "</i>"

    def __formatBold(self, string):
        return "<b>" + string + "</b>"

    def __formatUnderline(self, string):
        return "<u>" + string + "</u>"

    def __formatInQuotes(self, string):
        return "\"" + string + "\""

    def getMLAFormat(self):
        MLA_AUTHORS = self.__getMLAAuthors()
        MLA_TITLE = self.citationDict[TITLE]
        
        if not MLA_TITLE:
            MLA_TITLE = ""
        

        MLA_VOLUME = self.citationDict[VOLUM]
        if MLA_VOLUME: 
            MLA_VOLUME = "vol. " + MLA_VOLUME + ", "

        MLA_ISSUE = self.citationDict[ISSUE]

        MLA_PUBLICATION = self.citationDict[PBLCA]
        MLA_PUBLISHER = self.citationDict[PBLSH]
        MLA_PUBLICATION_CITY = self.citationDict[PBCTY]



        if MLA_PUBLISHER:
            if MLA_PUBLICATION:
                MLA_PUBLICATION = self.__formatItalic(MLA_PUBLICATION) + ", "
                MLA_PUBLISHER = MLA_PUBLISHER + ", "
            else:
                if self.citationDict[TYPE] == TYPE_BOOK:
                    MLA_PUBLISHER = MLA_PUBLISHER + ", "
                else:
                    MLA_PUBLISHER = self.__formatItalic(MLA_PUBLISHER) + ", "
        else:
            if MLA_PUBLICATION:
                MLA_PUBLICATION = self.__formatItalic(MLA_PUBLICATION) + ", "

        if MLA_PUBLICATION_CITY:
            MLA_PUBLICATION_CITY += ", "



        MLA_PAGES = self.citationDict[PAGES]

        MLA_PUBLICATIONDATE = self.__getMLAPublishingDateFormat()
        MLA_ACCESSDATE = self.__getMLAAccessDateFormat()

        MLA_URL = self.citationDict[URL]

        if MLA_URL:
            MLA_URL = self.citationDict[URL]+". "
            MLA_ACCESSDATE = "Accessed " + MLA_ACCESSDATE 

        else:
            MLA_URL = ""
            MLA_ACCESSDATE = ""


        
           
        ############################################################################
        #                           MLA BOOK FORMATTING
        ############################################################################
        if self.citationDict[TYPE] == TYPE_BOOK:
            MLA_TITLE = self.__formatItalic(MLA_TITLE+".")+" "
            MLA_PUBLICATIONDATE = self.citationDict['PBLYR'] + ". "

            if MLA_PAGES:
                MLA_PUBLICATIONDATE=MLA_PUBLICATIONDATE.replace(".",",")
                if "-" in MLA_PAGES or "," in MLA_PAGES:
                    MLA_PAGES = "pp. " + MLA_PAGES + ". "
                else:
                    MLA_PAGES = "p. " + MLA_PAGES + ". "
     


            # Since books don't have "issues", we use editions
            if MLA_ISSUE: 
                suffix=''

                # Suffixes to end numbers with (1st, 2nd, 3rd, 17th, 101st, etc.)
                if 4 <= int(MLA_ISSUE) <= 20:
                    suffix = 'th'
                elif int(MLA_ISSUE)%10 == 1:
                    suffix = 'st'
                elif int(MLA_ISSUE)%10 == 2:
                    suffix = 'nd'
                elif int(MLA_ISSUE)%10 == 3:
                    suffix = 'rd'
                else:
                    suffix = 'th'

                MLA_ISSUE = MLA_ISSUE + suffix + " ed., "

            if not MLA_URL:
                MLA_ACCESSDATE = ""


            finalStringList=[MLA_AUTHORS, MLA_TITLE, MLA_VOLUME, MLA_ISSUE, MLA_PUBLICATION_CITY, MLA_PUBLICATION, MLA_PUBLISHER, MLA_PUBLICATIONDATE, MLA_PAGES, MLA_URL, MLA_ACCESSDATE]

        ############################################################################
        #                   MLA CONFERENCE PAPER FORMATTING
        ############################################################################
        else:
            if not MLA_TITLE:
                MLA_TITLE = ""
            MLA_TITLE = self.__formatInQuotes(MLA_TITLE+".")+" "
            if MLA_ISSUE: 
                MLA_ISSUE = "no. " + MLA_ISSUE + ", "

            if MLA_PAGES:
                MLA_PAGES = "par. " + MLA_PAGES + ". "

            finalStringList=[MLA_AUTHORS, MLA_TITLE, MLA_VOLUME, MLA_ISSUE, MLA_PUBLICATION, MLA_PUBLISHER, MLA_PUBLICATIONDATE, MLA_PAGES, MLA_URL, MLA_ACCESSDATE]


        return "".join(finalStringList)

    def __getAPAAuthors(self):
        authtable = self.citationDict[AUTHT]
        authstring = ''

        if len(authtable) == 1:
            lname = authtable[0][LNAME]
            fname = authtable[0][FNAME]
            minit = authtable[0][MINIT]

            # If a name is provided
            if lname+fname+minit != "":
                # If last name given
                if lname:
                    # full last name is in output
                    authstring += lname
                    # if firstname given
                    if fname:
                        authstring += ', ' + fname[0]
                        # also middle initial
                        if minit:
                            authstring += '. ' + minit 

                # If first name, but no last name (ie, Cher, Adele, Oprah, The Rock)
                elif fname:
                    authstring += fname

                    
                    if minit:
                        authstring += ' ' + minit

            else:
                return ""



        #elif len(authtable) <= 3:
        else:
            lname = authtable[0][LNAME]
            fname = authtable[0][FNAME]
            minit = authtable[0][MINIT]
            
            if lname:
                authstring += lname
                if fname:
                    authstring += ', ' + fname[0] +'.'
                    if minit:
                        authstring += ' ' + minit + '.'
            elif fname:
                authstring += fname
                if minit:
                    authstring += ' ' + minit + '.'


            for i in range(1, len(authtable)):
                if i >= DefaultAPAMaxAuthors:
                    authstring += ", et al"
                    break
                if i == len(authtable)-1:
                    authstring += ' &'
                else:
                    authstring += ','

                lname = authtable[i][LNAME]
                fname = authtable[i][FNAME]
                minit = authtable[i][MINIT]

                if lname:
                    authstring += ' ' + lname
                    if fname:
                        authstring += ', ' + fname[0] + '.'
                        if minit:
                            authstring += ' ' + minit + '.'
                elif fname:
                    authstring += fname
                    if minit:
                        authstring += ' ' + minit + "."


        if authstring[-1] != '.':
            authstring += "."

        return authstring


    #################################################################
    # Get APA Format
    #################################################################
    def getAPAFormat(self):
        APA_AUTHORS = self.__getAPAAuthors()
        APA_TITLE = self.citationDict[TITLE]
        if APA_AUTHORS:
            APA_AUTHORS = APA_AUTHORS+" "

        if not APA_TITLE:
            APA_TITLE = ""


        APA_PUBLICATIONYEAR = None

        APA_TYPE = self.citationDict[TYPE]
        APA_PUBLICATION = self.citationDict[PBLCA]
        if APA_PUBLICATION:
            APA_PUBLICATION = self.__formatItalic(APA_PUBLICATION)


        APA_PUBLICATIONYEAR = self.getPublishingDateYear()


####### IF BOOK
        #print("TYPE",APA_TYPE, APA_TITLE, APA_AUTHORS,"\n")
        if APA_TYPE == TYPE_BOOK:
            APA_TITLE = self.__formatItalic(APA_TITLE)
            APA_PUBLICATIONYEAR = self.citationDict[PBLYR]
            APA_ISSUE = self.citationDict[ISSUE]

            if APA_ISSUE: 
                suffix=''

                # Suffixes to end numbers with (1st, 2nd, 3rd, 17th, 101st, etc.)
                if 4 <= int(APA_ISSUE) <= 20:
                    suffix = 'th'
                elif int(APA_ISSUE)%10 == 1:
                    suffix = 'st'
                elif int(APA_ISSUE)%10 == 2:
                    suffix = 'nd'
                elif int(APA_ISSUE)%10 == 3:
                    suffix = 'rd'
                else:
                    suffix = 'th'

                APA_ISSUE = APA_ISSUE + suffix + " ed."

            APA_VOLUME = self.citationDict[VOLUM]
            if APA_VOLUME:
                APA_VOLUME = "Vol. " + APA_VOLUME

            APA_ISSVOL = ""

            if APA_VOLUME and APA_ISSUE:
                APA_ISSUE += ", "
            if APA_VOLUME or APA_ISSUE:
                APA_ISSVOL = " (%s)"%(APA_ISSUE+APA_VOLUME) 
                


            if APA_PUBLICATIONYEAR:
                APA_PUBLICATIONYEAR = "(%s). "%str(APA_PUBLICATIONYEAR)

            APA_PAGES = self.citationDict[PAGES]

            if APA_PAGES:
                if "-" in APA_PAGES or "," in APA_PAGES:
                    APA_PAGES = " (pp. " + APA_PAGES + "). "
                else:
                    APA_PAGES = " (p. " + APA_PAGES + "). "

            else:
                if APA_ISSVOL:
                    APA_ISSVOL += ". "
                else:
                    APA_TITLE += ". "

            APA_PUBLISHER = self.citationDict[PBLSH]
            #print("\nAPA_PUBLISHER",APA_PUBLISHER, "APA_PAGES :|%s|"%APA_PAGES)
            #print("\n")
            if APA_PUBLISHER:
                APA_PUBLISHER += ". "

            #print("|%s|%s|%s|%s|%s|%s|"%(APA_TITLE,APA_ISSVOL,APA_PAGES,APA_PUBLICATIONYEAR,APA_PUBLISHER,APA_AUTHORS))

            if APA_AUTHORS:
                useList = [i for i in [APA_AUTHORS, APA_PUBLICATIONYEAR, APA_TITLE, APA_ISSVOL, APA_PAGES, APA_PUBLISHER] if i]
                return "".join(useList)
            else:
                useList = [i for i in [APA_TITLE, APA_ISSVOL, APA_PAGES,APA_PUBLICATIONYEAR, APA_PUBLISHER] if i]
                return "".join(useList)
            
     



########IF TYPE is ARTICLE
        elif APA_TYPE == TYPE_ARTICLE:
            APA_ISSUE = self.citationDict[ISSUE]
            APA_VOLUME = self.citationDict[VOLUM]

            APA_ISSVOL = ""

            if APA_VOLUME and APA_ISSUE:
                APA_ISSVOL = "<i>, %s</i>(%s)"%(APA_VOLUME, APA_ISSUE) 
            elif APA_ISSUE:
                APA_ISSVOL = "<i>,</i> (%s)"%(APA_ISSUE)
            elif APA_VOLUME:
                APA_ISSVOL = "<i>, %s</i>"%(APA_VOLUME)
            else:
                pass
            print("APA VOL ISS: (%s, %s, %s)"%(APA_VOLUME,APA_ISSUE, APA_ISSVOL))
                

            if APA_PUBLICATIONYEAR:
                APA_PUBLICATIONYEAR = "(%s). "%str(APA_PUBLICATIONYEAR)


            APA_PAGES = self.citationDict[PAGES]

            if APA_PAGES:
                if APA_ISSVOL:
                    APA_ISSVOL += ","
                else:
                    APA_TITLE += ","

                APA_PAGES = " " + APA_PAGES + "."

            else:
                if APA_ISSVOL:
                    APA_ISSVOL += ". "
                else:
                    APA_TITLE += ". "

            APA_URL = self.citationDict[URL]
            if APA_URL:
                APA_URL = " " + self.__formatBold(APA_URL)



            if APA_AUTHORS:
                useList = [i for i in [APA_AUTHORS, APA_PUBLICATIONYEAR, APA_TITLE, APA_PUBLICATION, APA_ISSVOL, APA_PAGES, APA_URL] if i]
                return "".join(useList)

            else:
                useList = [i for i in [APA_TITLE, APA_PUBLICATION, APA_ISSVOL, APA_PUBLICATIONYEAR, APA_PAGES, APA_URL] if i]
                return "".join(useList)

####### CON PAPER
        else:
            APA_AUTHORS

            APA_PUBLICATIONYEAR = self.getPublishingDateYear()
            APA_PUBLICATIONMONTH = self.getPublishingDateMonthFull()
            APA_PUBLICATIONDAY = self.getPublishingDateDay()
            APA_CON_DATE = ""

            if APA_PUBLICATIONYEAR:
                APA_CON_DATE += APA_PUBLICATIONYEAR
                if APA_PUBLICATIONMONTH:
                    APA_CON_DATE += ", " + APA_PUBLICATIONMONTH
                    if APA_PUBLICATIONDAY not in ["00",""]:
                        APA_CON_DATE += " " + str(int(APA_PUBLICATIONDAY))
                APA_CON_DATE = " (%s)."%APA_CON_DATE



            if not APA_TITLE:
                APA_TITLE = ""


            APA_TITLE = self.__formatItalic(APA_TITLE)+" [Paper presentation]"

            APA_PUBLISHER = self.citationDict[PBLSH]
            APA_PUBCITY = self.citationDict[PBCTY]

            APA_CON_LOC = ""

            if APA_PUBCITY:
                APA_PUBLISHER += ", "
                APA_PUBCITY += "."
            else:
                APA_PUBLISHER += "."

            if APA_PUBCITY or APA_PUBLISHER:
                APA_CON_LOC = " "+APA_PUBLISHER+APA_PUBCITY

            APA_URL = self.citationDict[URL]
            if APA_URL:
                APA_URL = " " + APA_URL 

            if APA_AUTHORS:
                APA_TITLE = " " + APA_TITLE + "."
                useList = [i for i in [APA_AUTHORS, APA_CON_DATE, APA_TITLE, APA_CON_LOC, APA_URL] if i]
                return "".join(useList)

            else:
                useList = [i for i in [APA_TITLE, APA_CON_DATE, APA_CON_LOC, APA_URL] if i]
                return "".join(useList)



    def __getIEEEAuthors(self):
        authtable = self.citationDict[AUTHT]
        authstring = ''

        if len(authtable) == 1:
            lname = authtable[0][LNAME]
            fname = authtable[0][FNAME]
            minit = authtable[0][MINIT]

            if lname+fname+minit != "":
                if fname:
                    authstring += fname[0] + "."
                    
                    if minit:
                        authstring += minit[0] + "."

                    if lname:
                        lname = " " + lname

                if lname:
                    authstring += lname

            else:
                return ""



        else:
            lname = authtable[0][LNAME]
            fname = authtable[0][FNAME]
            minit = authtable[0][MINIT]

            if lname+fname+minit != "":
                if fname:
                    authstring += fname[0] + "."
                    
                    if minit:
                        authstring += minit[0] + "."

                    if lname:
                        lname = " " + lname

                if lname:
                    authstring += lname

            else:
                return ""

            for i in range(1, len(authtable)):
                if i >= DefaultIEEEMaxAuthors:
                    authstring += " et al"
                    break
                if i == len(authtable)-1:
                    if authstring[-1] == ",":
                        authstring=authstring[0:-1]
                    authstring += ' and'
                else:
                    authstring += ','

                lname = authtable[i][LNAME]
                fname = authtable[i][FNAME]
                minit = authtable[i][MINIT]

                if lname+fname+minit != "":
                    authstring += " "
                    if fname:
                        authstring += fname[0] + "."
                        
                        if minit:
                            authstring += minit[0] + "."

                        if lname:
                            lname = " " + lname

                    if lname:
                        authstring += lname


        if authstring[-1] != '.':
            authstring += ""

        return authstring



    def getIEEEFormat(self):
        IEEE_TYPE = self.citationDict[TYPE]

        IEEE_AUTHORS = self.__getIEEEAuthors()
        IEEE_TITLE = self.citationDict[TITLE]

        IEEE_PUBLICATION = self.citationDict[PBLCA]
        IEEE_VOLUME = self.citationDict[VOLUM]
        IEEE_ISSUE = self.citationDict[ISSUE]

        IEEE_CITY = self.citationDict[PBCTY]
        IEEE_PUBLISHER = self.citationDict[PBLSH]

        IEEE_CITY_PUB = ""

        if IEEE_CITY and IEEE_PUBLISHER:
            if IEEE_TYPE == TYPE_CONFERENCE_PAPER:
                IEEE_CITY += ", "
            else:
                IEEE_CITY += ": "

        IEEE_CITY_PUB = IEEE_CITY + IEEE_PUBLISHER
            

        IEEE_PUBDATE_YEAR = self.getPublishingDateYear()
        IEEE_PUBDATE_MONTH = self.getPublishingDateMonthAbbreviation()
        IEEE_PUBDATE_DAY = self.getPublishingDateDay()
        
        IEEE_PAGES = self.citationDict[PAGES]

        IEEE_ACCESS_YEAR = self.getAccessDateYear()
        IEEE_ACCESS_MONTH = self.getAccessDateMonthAbbreviation()
        IEEE_ACCESS_DAY = self.getAccessDateDay()

        IEEE_ACCESS_DATE_STRING = ""
        
        if IEEE_ACCESS_MONTH:
            IEEE_ACCESS_DATE_STRING += IEEE_ACCESS_MONTH+" "

        if IEEE_ACCESS_DAY:
            IEEE_ACCESS_DATE_STRING += str(int(IEEE_ACCESS_DAY))+", "

        IEEE_ACCESS_DATE_STRING += IEEE_ACCESS_YEAR
        IEEE_ACCESS_DATE_STRING = "Accessed: "+IEEE_ACCESS_DATE_STRING+"."





        IEEE_URL = self.getURL()

        if IEEE_URL:
            IEEE_URL = "[Online]. Available: " + IEEE_URL

        if not IEEE_TITLE:
            IEEE_TITLE = ""

        

        if IEEE_TYPE == TYPE_BOOK:
            print("\n\n__________________________________________")
            IEEE_PUBDATE_YEAR = self.citationDict[PBLYR]

            if IEEE_VOLUME:
                IEEE_VOLUME = "vol. " + IEEE_VOLUME

            if IEEE_ISSUE: 
                suffix=''

                # Suffixes to end numbers with (1st, 2nd, 3rd, 17th, 101st, etc.)
                if 4 <= int(IEEE_ISSUE) <= 20:
                    suffix = 'th'
                elif int(IEEE_ISSUE)%10 == 1:
                    suffix = 'st'
                elif int(IEEE_ISSUE)%10 == 2:
                    suffix = 'nd'
                elif int(IEEE_ISSUE)%10 == 3:
                    suffix = 'rd'
                else:
                    suffix = 'th'

                IEEE_ISSUE = IEEE_ISSUE + suffix + " ed."


            #print([IEEE_AUTHORS,IEEE_TITLE,IEEE_PUBLICATION,IEEE_VOLUME,IEEE_ISSUE, IEEE_CITY_PUB, IEEE_PUBDATE_YEAR, IEEE_ACCESS_DATE_STRING])

            finalStr = ""

            if IEEE_AUTHORS:
                finalStr += IEEE_AUTHORS + ", "


            finalStr += self.__formatItalic(IEEE_TITLE)+", "

            if IEEE_VOLUME:
                finalStr += IEEE_VOLUME + ", "
            
            if IEEE_ISSUE:
                finalStr += IEEE_ISSUE + " "

            finalStr += IEEE_CITY_PUB

            finalStr += ", " + IEEE_PUBDATE_YEAR + ". "
            if IEEE_URL:
                finalStr += IEEE_URL + " " + IEEE_ACCESS_DATE_STRING

            return finalStr
            

                
            
        if IEEE_TYPE == TYPE_ARTICLE:

            finalStr = ""

            if IEEE_AUTHORS:
                finalStr += IEEE_AUTHORS + ", "

            finalStr += self.__formatInQuotes(IEEE_TITLE+",")+" "

            if IEEE_PUBLICATION:
                finalStr += self.__formatItalic(IEEE_PUBLICATION+", ")

            if IEEE_VOLUME:
                finalStr += "vol. " + IEEE_VOLUME + ", "
            
            if IEEE_ISSUE:
                finalStr += "no. " + IEEE_ISSUE + ", "
                
            if IEEE_PAGES:
                if "-" in IEEE_PAGES or "," in IEEE_PAGES:
                    IEEE_PAGES = "pp. " + IEEE_PAGES
                else:
                    IEEE_PAGES = "p. " + IEEE_PAGES

                if IEEE_PUBDATE_YEAR:
                    IEEE_PAGES += ", "
 
                finalStr += IEEE_PAGES

            if IEEE_PUBDATE_YEAR:
                cleanStr = ""
                if IEEE_PUBDATE_MONTH:
                    cleanStr+=IEEE_PUBDATE_MONTH
                    if IEEE_PUBDATE_DAY not in ["", "00"]:
                        cleanStr+=" "+str(int(IEEE_PUBDATE_DAY))
                    cleanStr+=", "
                cleanStr+=IEEE_PUBDATE_YEAR
                finalStr += cleanStr + ". "
            else:
                finalStr += IEEE_PUBDATE_YEAR + ". "

            if IEEE_URL:
                finalStr += IEEE_URL + " " + IEEE_ACCESS_DATE_STRING

            #print(finalStr)
            return finalStr
            
############# CONFERENCE PAPER ############
        else:
            finalStr = ""

            if IEEE_AUTHORS:
                finalStr += IEEE_AUTHORS + ", "

            if not IEEE_TITLE:
                IEEE_TITLE = ""

            finalStr += self.__formatInQuotes(IEEE_TITLE+",")

            if IEEE_PUBLISHER:
                finalStr += " presented at " + IEEE_PUBLISHER

            if IEEE_CITY:
                finalStr += ", " + IEEE_CITY

                
            if IEEE_PAGES:
                if "-" in IEEE_PAGES or "," in IEEE_PAGES:
                    IEEE_PAGES = "pp. " + IEEE_PAGES
                else:
                    IEEE_PAGES = "p. " + IEEE_PAGES

                if IEEE_PUBDATE_YEAR:
                    IEEE_PAGES += ", "
 
                finalStr += IEEE_PAGES

            if IEEE_PUBDATE_YEAR:
                cleanStr = ""
                if IEEE_PUBDATE_MONTH:
                    cleanStr+=IEEE_PUBDATE_MONTH
                    if IEEE_PUBDATE_DAY not in ["", "00"]:
                        cleanStr+=" "+str(int(IEEE_PUBDATE_DAY))
                    cleanStr+=", "
                cleanStr+=IEEE_PUBDATE_YEAR
                finalStr += cleanStr + ". "
            else:
                finalStr += IEEE_PUBDATE_YEAR + ". "


            if IEEE_URL:
                finalStr += IEEE_URL + " " + IEEE_ACCESS_DATE_STRING

            #print(finalStr)
            return finalStr
        


            

            

 
            
mainCiteManager = CitationManager()
#mainCiteManager.readInDatabaseFromFile(template=True)
#mainCiteManager.readInDatabaseFromFile()
#mainCiteManager.readInDatabaseFromFile('./User Databases/citations.xct')

mainCiteManager.readInDatabaseFromFile(newfile=True)


'''
cit = Citation({TYPE  : TYPE_BOOK,  
                TITLE : "Court of Owls", 
                AUTHT : {0:{LNAME : "Grayson", FNAME : "Richard", MINIT : "M"}},
                VOLUM : "2", 
                ISSUE : "3", 
                PAGES : "2,3", 
                PBLCA : "", 
                PBLSH : "Random House", 
                PBLDT : "", 
                PBLYR : "2000", 
                PBCTY : "Gotham, NY", 
                ACCDT : "08/12/2022", 
                URL   : "http://www.coo.com"})


cit.addAuthor("King","Stephen","")
cit.addAuthor("Atkerson","Benjamin","T")
'''
