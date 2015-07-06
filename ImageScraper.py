'''
Created on Nov 25, 2013

@author: byanamadala
'''
from datetime import *

import urllib2
import unicodedata
import re, htmlentitydefs
import os, sys
from SolutionGridExtractor import *
import StringIO
from PIL import Image
import puz
import logging

def getResponseString(URL):
    htmlStr = None
    try:
        response = urllib2.urlopen(URL)
        htmlStr = response.read()
    except Exception as e:
        print 'exception reaching URL %s %s %s' %(URL)
        raise(e)
    return htmlStr

def getNextSolutionDate(puzDate):
    weekday = puzDate.weekday()
    if weekday == 6:
        return puzDate + timedelta(days=7)
    elif weekday == 5:
        return puzDate + timedelta(days=2)
    else:
        return puzDate + timedelta(days=1)

def getPageURL(primaryDate):
    if primaryDate > date(2006,1,1):
        fullURL = r'http://www.thehindu.com/archive/print/'+ primaryDate.strftime(r'%Y/%m/%d/') +r'#miscelaneous'
    else:
        fullURL = r'http://www.hindu.com/thehindu/'+ primaryDate.strftime(r'%Y/%m/%d/')+'10hdline.htm'
    return fullURL
    
def getCrosswordURL(pageURL, urltype='puzzle', puzzleNum=None):
    logging.debug('Getting URL for %s at %s' %(urltype, pageURL))
    htmlStr = getResponseString(pageURL)
    logging.debug('Received HTML Response, searching for patterns')
    if htmlStr is None:
        return None

    xWordURL = re.search(r'<a.*?>The\s?\s?Hindu\s?\s?Crossword\s?\s?.*?</a>', htmlStr)
    
    if xWordURL is None:
        return None

    xWordURL = xWordURL.group(0).split('"')[-2]
    xWordURLList = pageURL.split('/')[:-1]
    
    if not xWordURL.startswith('http'):
        xWordURLList.append(xWordURL)
        xWordURL='/'.join(xWordURLList)
    if puzzleNum is not None:
        oldXWordSolURL = re.search(r'<a.*?>Solution\s?\s?to\s?\s?Puzzle.*?'+str(puzzleNum)+'.*?</a>', htmlStr)
        newXWordSolURL = re.search(r'<a.*?>Solution No.*?'+str(puzzleNum)+'.*?</a>', htmlStr)
    else:
        oldXWordSolURL = re.search(r'<a.*?>Solution\s?\s?to\s?\s?Puzzle.*?</a>', htmlStr)
        newXWordSolURL = re.search(r'<a.*?>Solution No .*?</a>', htmlStr)
        
    if oldXWordSolURL is not None:
        oldXWordSolURL=oldXWordSolURL.group(0).split('"')[1]
        xWordURLList.append(oldXWordSolURL)
        oldXWordSolURL='/'.join(xWordURLList)
    
    if newXWordSolURL is not None:
        newXWordSolURL=newXWordSolURL.group(0).split('"')[1]
    
    if urltype != 'puzzle':
        if oldXWordSolURL is not None:
            return oldXWordSolURL
        elif newXWordSolURL is not None:
            return newXWordSolURL
    logging.debug('Pattern Found: %s' %(xWordURL))
    return xWordURL

def getImageFromURL(URL):
    file = StringIO.StringIO(urllib2.urlopen(URL).read())
    img = Image.open(file)
    return img

def getImageURLs(htmlString):
    #### TODO
    # needs to work with patterns found in page http://www.thehindu.com/todays-paper/tp-miscellaneous/the-hindu-crossword-11436/article7373825.ece
    # use the carousel div to identify the image rather than using the cross word string.
    imgPatterns = re.finditer(r'<img src="http://www.thehindu.com/multimedia/dynamic/.*?CROSS.*?.jpg\s?".*?"/>', htmlString, flags=re.IGNORECASE)
    images = []
    for img in imgPatterns:
        images.append(img.group(0).split('"')[1])
    return images

def getCluesFromHTML(htmlString):
    puzzleHTML =htmlString.replace('\n', '')
    puzzleHTML =puzzleHTML.replace('\r', '')

    clues = re.findall(r'<p class="body">.*?</p>', puzzleHTML)
    clues = [x[16:-4].replace('<b>', '').replace('</b>','') for x in clues]
    
    AcrossClues = []
    DownClues = []
    for clue in clues:
        if clue.strip().upper() == 'ACROSS':
            clueType = 'ACROSS'
            continue
        elif clue.strip().upper() == 'DOWN':
            clueType = 'DOWN'
            continue
        else:
            if clueType == 'ACROSS':
                AcrossClues.append(clue)
            else:
                DownClues.append(clue)
    cluePattern = re.compile("[0-9]{1,2}.*?\([0-9,\-]*.?\)")
    AcrossCluesRE = re.finditer(cluePattern, " ".join(AcrossClues))
    DownCluesRE = re.finditer(cluePattern, " ".join(DownClues))
    AcrossClues = []
    DownClues = []
    for item in AcrossCluesRE:
        AcrossClues.append((item.group(0), 'ACROSS'))
    for item in DownCluesRE:
        DownClues.append((item.group(0), 'DOWN'))
#     AcrossClues = [ (x + ')', 'ACROSS') for x in "".join(AcrossClues).split(')') if x.strip() != '']
#     DownClues = [ (x + ')', 'DOWN') for x in "".join(DownClues).split(')') if x.strip() != '']
    clues = AcrossClues
    clues.extend(DownClues)
    
    clues = Clues(clues)
    return clues

def validateSolution(solution):
    splitSolution = solution.split('\n')
    splitSolution = [x for x in splitSolution if x !='']
    for line in splitSolution:
        if len(line) != 15:
            raise Exception("Rejected Solution \n" +solution)


def unescape(text):
    def fixup(m):
        text = m.group(0)
        charMapDict = {'&#8220;':'"',
                       '&#8221;':'"',
                       '&#8216;':"'",
                       '&#8217;':"'",
                       '&#8230;':"...",
                       '&#8212': "-"}
        if text in charMapDict.keys():
            return charMapDict[text]
        return text
#         text = m.group(0)
#         if text[:2] == "&#":
#             # character reference
#             try:
#                 if text[:3] == "&#x":
#                     return unicodedata.normalize('NKFD', unichr(int(text[3:-1], 16)))
#                 else:
#                     return unicodedata.normalize('NKFD', unichr(int(text[2:-1])))
#             except ValueError:
#                 pass
#         else:
#             # named entity
#             try:
#                 text = unicodedata.normalize('NKFD', unichr(htmlentitydefs.name2codepoint[text[1:-1]]))
#             except KeyError:
#                 pass
#         return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

CLUETYPE= {'ACROSS' : 0, 'DOWN': 1}

class Clue(object):
    __slots__ =  ('type','position', 'clue', 'spaces')
    
    def __init__(self, clueString, type):
        for field in self.__slots__:
            setattr(self, field, None)
        self.type = type.upper()
        rawClue = clueString.strip()
        for n in range(2,0,-1):
            if (not rawClue[0:n].strip().isalpha()):
                try:
                    self.position = int(rawClue[0:n].strip())
                except ValueError:
                    continue
                
                self.spaces = '(' + rawClue.split('(')[-1]
                uniClueStr = unescape(rawClue[n:-1*len(self.spaces)].strip())
                self.clue = uniClueStr.encode('ascii', 'ignore') 
                break

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __hash__(self):
        return self.position * 1000 + CLUETYPE[self.type]

    def __cmp__(self, other):
        ''' compare with other strategy or tuple '''
        # None is treated as 0
        if isinstance(other, Clue): 
            if self.__hash__() == other.__hash__():
                return 0
            elif self.__hash__() > other.__hash__():
                return 1
            elif self.__hash__() < other.__hash__():
                return -1
        raise TypeError('Cannot compare type %s and %s' % (type(self), type(other)))
    
    def as_str(self, separator='\n', show_name=True):
        ''' displays objects as name=value pairs separated by
            character separator
        '''
        output = []
        for field in self.__slots__:
            value = getattr(self, field, None)
            valueFormat = '%s'
            if show_name:
                valueFormat = ('%s=' % field) + valueFormat
            output.append(valueFormat % str(value))
        return separator.join(output)
    
    def __str__(self):
        return self.as_str(' ', False)

class Clues(list):
    
    containedClass = Clue
    
    def __init__(self, clueList):
        for inputData in clueList:
            if isinstance(inputData, tuple):
                self.append(self.containedClass(*inputData))
            elif isinstance(inputData, type(self.containedClass)):
                self.append(inputData)
            else:
                raise TypeError('Unknown Input type %s need a list of Strings or Clue objects'% (type(inputData)))
            self.sort()
    
    def getPuzClues(self):
        output = []
        for item in self:
            output.append(item.clue + ' ' + item.spaces)
        return output

    def as_str(self, separator=', ', show_header=True, indent=''):
        ''' Used to print a table with names of the field as a header row
            and subsequent rows contain the values all separated by commas
        '''
        nameStr = ''
        return nameStr + '\n'.join(
            indent + item.as_str(separator, False) for item in self)
    
    def __str__(self):
        return self.as_str(' ', False, '\t')

class ImageScraper(object):
    puzzle = None
    solution = None
    clues = None
    puzzleDate = None
    number = None
    solutionDate = None
    puzzleURL = None
    solutionURL = None
    puzzleImage = None
    solutionImage = None

    def __init__(self, puzzleDate=date.today(), solutionDate=None):
        '''
        
        '''
        logging.debug('Started processing puzzle for date %s' % puzzleDate)
        self.puzzleDate = puzzleDate
        self.solutionDate = solutionDate
        self.setPuzzleURL()
        self.setSolutionURL()
        self.setPuzzleNumberCluesImage()
        self.setSolutionImage()
        self.setPuzzleString()
        self.setSolutionString()
        
    def setPuzzleURL(self):
        pageURL = getPageURL(self.puzzleDate)
        self.puzzleURL = getCrosswordURL(pageURL, 'puzzle')
        logging.debug('Puzzle URL %s' % self.puzzleURL)

    def setPuzzleNumberCluesImage(self):
        number = 0
        if self.puzzleURL is None:
            self.number = number
            return
        logging.debug('Retrieving puzzle from the URL %s' % self.puzzleURL)
        puzzleHtml = getResponseString(self.puzzleURL)
        logging.debug('Puzzle HTML received, searching for Crossword Number')
        numPattern = re.search(r'The\s\s?Hindu\s\s?Crossword.*?[0-9]{2,5}', puzzleHtml)
        if numPattern is not None:
            number = int(numPattern.group(0).split(' ')[-1])
            logging.debug('Number found - Crossword Number %d' %(number))
        self.number = number
        logging.debug('Searching for Images')
        images = getImageURLs(puzzleHtml)
        logging.debug('%d Images found' %(len(images)))
        if len(images) > 0:
            self.puzzleImage = min(*tuple(images))
            logging.debug('Puzzle Image set to %s' %(self.puzzleImage))
        logging.debug('Searching for Clues')
        self.clues = getCluesFromHTML(puzzleHtml)
        logging.debug('Clue search completed!')
        
    
    def setPuzzleString(self):
        if self.puzzleImage is None:
            return
        puzImage = getImageFromURL(self.puzzleImage)
        puzzleStr = parsePuzzleImage(puzImage)
        self.puzzle = puzzleStr

    def setSolutionString(self):
        if self.puzzle is None:
            return
        elif self.solutionImage is None:
            self.solution = self.puzzle.replace('_','X')
        else:
            solImage = getImageFromURL(self.solutionImage)
            solStr = parseSolutionImage(solImage)
            validateSolution(solStr)
#             if len(solStr.replace('\n', '')) != len(self.puzzle.replace('\n','')):
#                 "Rejected Solution \n" +solStr
#             solStr = self.puzzle.replace('_','X')
            self.solution = solStr
        

    def setSolutionImage(self):
        if self.solutionURL is None:
            logging.debug('No solution URL found!')
            return
        solutionHtml = getResponseString(self.solutionURL)
        logging.debug('Solution HTML received, searching for Images')
        images = getImageURLs(solutionHtml)
        logging.debug('Images found %d' %(len(images)))
        if len(images) > 1:
            self.solutionImage = images[1]
            logging.debug('Solution Image found %s' %(self.solutionImage))
        elif len(images) > 0:
            self.solutionImage = images[0]
            logging.debug('Solution Image (suspect) %s' %(self.solutionImage))
        else:
            logging.debug('Could not find Solution Image')
        
        
    def setSolutionURL(self):
        solutionDateUndetermined = (self.puzzleURL is not None) and (self.solutionDate is None)
        if solutionDateUndetermined:
            logging.debug('Solution URL is undetermined - trying to guess the solution date!!!')
            self.solutionDate = getNextSolutionDate(self.puzzleDate)
            for tries in xrange(5):
                logging.debug('Guess # %d using solutionDate %s' %(tries, self.solutionDate))
                if self.solutionDate > date.today():
                    logging.debug('Solution not yet published!!!')
                    break
                pageURL = getPageURL(self.solutionDate)
                self.solutionURL = getCrosswordURL(pageURL, 'solution', self.number)
                if self.solutionURL is not None:
                    break
                self.solutionDate= getNextSolutionDate(self.solutionDate)
        logging.debug('Solution URL %s' % self.solutionURL)
        if self.solutionURL is None:
            raise Exception('No Solution Available')

    def exportToPuz(self, filename=None):
        #p = puz.read('Crypt.puz')
        p=puz.Puzzle()
        p.puzzletype = puz.PuzzleType.Normal
        p.title = 'The Hindu Crossword No. %s' % ( str(self.number))
        p.copyright = u'Copyright ' + self.puzzleDate.strftime(r'%Y/%m/%d') +', The Hindu'
        p.author=''
        p.width = 15
        p.height = 15
        p.fill = self.puzzle.replace('\n','').replace('#','.').replace('_','-')
        if self.solution is not None:
            p.solution = self.solution.replace('\n','').replace('#','.')
        else:
            p.solution = p.fill.replace('-','X')

        p.clues = self.clues.getPuzClues()
        if filename is None:
            filename = os.path.join(os.path.dirname(__file__),'puzzles', 'puzfiles',str(self.number)+'.puz')
        puzFile=open(filename, 'wb')
        puzFile.write(p.tobytes())
        puzFile.close()

    def as_str(self, indent=''):
        out = []
        msg = 'The Hindu Crossword No. %s' % ( str(self.number))
        out.append(indent + msg)
        msg = 'Puzzle Dated %s' 
        out.append(indent + msg % (self.puzzleDate))
        msg = 'Puzzle URL %s' 
        out.append(indent + msg % (self.puzzleURL))
        if self.puzzleImage is not None:
            msg = 'puzzle Image %s' 
            out.append(indent + msg % (self.puzzleImage))
        if self.solutionURL is not None:
            msg = 'Solution Date %s' 
            out.append(indent + msg % (self.solutionDate))
            msg = 'Solution URL %s' 
            out.append(indent + msg % (self.solutionURL))
        if self.solutionImage is not None:
            msg = 'Solution Image %s' 
            out.append(indent + msg % (self.solutionImage))
        if self.puzzle is not None:
            out.append("")
            msg = 'Puzzle grid \n%s'
            if self.solution is not None:
                gridStr= enhancedPuzzleString(self.puzzle, self.solution)
            else:
                gridStr= enhancedPuzzleString(self.puzzle)
                gridStr = gridStr.replace('\n', '\n'+indent)
            out.append(msg %gridStr)
        if self.clues is not None:
            out.append("")
            msg = 'Clues \n%s'
            out.append(indent + msg %(self.clues.as_str('  ', False, indent)))
        return '\n'.join(out)

    def __str__(self):
        return self.as_str()
    

if __name__ == '__main__':
    import timeit
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)-26s %(levelname)-8s %(message)s')
#     startDate = date.today()
    startDate = date(2015,7,2)
#     print startDate
    for day in (startDate - timedelta(n) for n in range(100)):
        try:
            starttime = datetime.now()
            print 'Processing crossword for day : %s' % (day)
            I = ImageScraper(day)
            print I
            I.exportToPuz()
        except Exception as e:
            logging.exception(e)
            pass
        finally:
            print
            print "Time Taken : " + str(datetime.now() - starttime)
            print
#          
#     startDate = date.today()
#     #startDate = date(2013,11,23)
#     for day in (startDate - timedelta(n) for n in range(100)):
#         print ImageScraper(day)
#         print

#     I=ImageScraper(date(2015,7,3))
#     print I
#     I.exportToPuz()
#    print ImageScraper(date(2013,5,19))
#    print 
#    print ImageScraper(date(2003,5,19))
#    print 
#    print ImageScraper(date(2006,1,1))
     
