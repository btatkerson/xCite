from random import choice
import datetime

AcceptableNameChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'-. "
LabeledWidgetsDict = {}
SharedObjects = {}

TYPE  = "TYPE"  # Type of entry - Book, paper, article
TITLE = "TITLE" # Title of content
LNAME = "LNAME" # Last name
FNAME = "FNAME" # First Name
MINIT = "MINIT" # Middle initial
VOLUM = "VOLUM" # Volume
ISSUE = "ISSUE" # Issue
PAGES = "PAGES" # Pages ("3", "3, 55", or "3 - 55")
PBLCA = "PBLCA" # Publication
PBLSH = "PBLSH" # Publisher
PBLDT = "PBLDT" # Publication Date
PBLYR = "PBLYR" # Publication Year
PBCTY = "PBCTY" # Publication City
ACCDT = "ACCDT" # Access Date
PBLDF = "PBLDF" # Publishing Date Format
URL   = "URL"   # URL if available
ATOSV = "ATOSV" # Autosave records 

DIALG = "DIALG" # Dialog message box
RECRD = "RECRD" # Record Pane

NOAUT = "NOAUT" # Number of Authors
AUTHT = "AUTHT" # Author table

INPUT = "INPUT" # Input Form

# Record Sheet filters
TYPEF = "TYPEF"  # Type of entry filter - Book, paper, article
FILTI = "FILTI" # Title Filter
FILLN = "FILLN" # Last Name Filter
FILFN = "FILFN" # First Name Filter
FILMI = "FILMI" # Middle Initial Filter
EXCTF = "EXCTF" # Exact Match for Filter
ENBLF = "ENBLF" # Are filters enabled checkbox

CTDSP = "CTDSP" # Citation Display
CITEF = "CITEF" # Citation Format Type

TYPE_ARTICLE = "Article"
TYPE_BOOK = "Book"
TYPE_CONFERENCE_PAPER = "Conference Paper"

CONTENT_TYPE={0: TYPE_ARTICLE,
              1: TYPE_BOOK,
              2: TYPE_CONFERENCE_PAPER}


CITATION_FORMAT_TYPE_MLA = "MLA"
CITATION_FORMAT_TYPE_APA = "APA"
CITATION_FORMAT_TYPE_IEEE = "IEEE"

CITATION_FORMAT_TYPE = {i:j for i,j in enumerate([CITATION_FORMAT_TYPE_MLA,CITATION_FORMAT_TYPE_APA, CITATION_FORMAT_TYPE_IEEE])}

DATE_MONTH_MAX_DAY = {0:0,
                      1:31,
                      2:29,
                      3:31,
                      4:30,
                      5:31,
                      6:30,
                      7:31,
                      8:31,
                      9:30,
                      10:31,
                      11:30,
                      12:31}
  
# May, June, and July are written out because May isn't and abbreviation and
# since "." would be a forth character anyhow.

DATE_MONTH_ABBREVIATION={0:"",
                         1:"Jan.",
                         2:"Feb.",
                         3:"Mar.",
                         4:"Apr.",
                         5:"May",
                         6:"June",
                         7:"July",
                         8:"Aug.",
                         9:"Sep.",
                         10:"Oct.",
                         11:"Nov.",
                         12:"Dec."}


DATE_MONTH_FULL={0:"",
                 1:"January",
                 2:"February",
                 3:"March",
                 4:"April",
                 5:"May",
                 6:"June",
                 7:"July",
                 8:"August",
                 9:"September",
                 10:"October",
                 11:"November",
                 12:"December"}

VALID_APPLICATION_TITLES = ["xCite Citation Manager",
                            "CiTerminator",
                            "CiTerminator 2: Judgement Day",
                            "ParaCite",
                            "Cight Flub",
                            "Camp Cite"]

WARNING_COLOR = '#ff0000'
YIELD_COLOR = '#CFBC30'

MinWindowWidth = 640
MinWindowHeight = 480
#DefaultWindowSize = [800,600]
DefaultWindowSize = [1152+256,864]
DefaultLabelWidthColA = 220
DefaultLabelWidthColB = 180
DefaultLabelBoxHeights = 50
DefaultMessageBoxHeight = 100
DefaultCitationFormatOutputTypeWidth = 200
DefaultCitationFormatOutdentation = 40

DefaultCleanFile = './core/conf/empty.xct'
DefaultTemplateFile = './core/conf/template.xct'
DefaultFileInput = './User Databases/citations.xct'
DefaultFileOutput = './User Databases/citations.xct'

DefaultDateFormat = 7 # 2022, Jan 1 format
DefaultFilterLabelText = 160
DefaultMLAMaxAuthors = 3
DefaultAPAMaxAuthors = 3
DefaultIEEEMaxAuthors = 6
DefaultTypeOfContent = TYPE_ARTICLE
DefaultDate = datetime.datetime.today().strftime("%m/%d/%Y")

'''
Date Formats: 
    0. Jan 2, 2022 
    1. January 2, 2022 
    2. 01/02/2022 
    3. 01/02/22 
    4. 1/2/22
    5. 2022/01/02
    6. 2022/1/2
    7. 2022, Jan 2
    8. 2022, January 2
    9. 01-02-2022
    10. 01-02-22
    11. 1-2-22
    12. 2022-01-02
    13. 2022-1-2
'''

