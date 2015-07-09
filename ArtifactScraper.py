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
import yaml

def loadYamlFile(filename):
    with open(filename, 'r') as cf:
        yamlDoc = yaml.load(cf)
    return yamlDoc

def writeYamlDocToFile(yamlDoc, filename):
    with open(filename, 'w') as cf:
        cf.write(yaml.dump(yamlDoc, default_flow_style=True))

def getResponseString(URL):
    htmlStr = None
    try:
        response = urllib2.urlopen(URL)
        htmlStr = response.read()
    except Exception as e:
        print 'exception reaching URL %s' %(URL)
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


def getImageURLs(htmlString):
    #### TODO
    # needs to work with patterns found in page http://www.thehindu.com/todays-paper/tp-miscellaneous/the-hindu-crossword-11436/article7373825.ece
    # use the carousel div to identify the image rather than using the cross word string.
#     imgPatterns = re.finditer(r'<img src="http://www.thehindu.com/multimedia/dynamic/.*?CROSS.*?.jpg\s?" height="400".*?"/>', htmlString, flags=re.IGNORECASE)
    splitString = htmlString.split(r'''<div class="jcarousel-wrapper">''')[1]
    splitString = splitString.split(r'''<script type="text/javascript">''')[0]
    imgPatterns = re.finditer(r'<img src="http://www.thehindu.com/multimedia/dynamic/.*?.jpg\s?".*?"/>', splitString, flags=re.IGNORECASE)
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
    return clues


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


class ArtifactScraper(object):
    pageDate = None
    pageURL = None
    puzzleNumber = None
    solutionNumber = None
    clues = None
    pageImages = []

    def __init__(self, pageDate=date.today()):
        '''
        
        '''
        self.pageDate = pageDate
        self.setPuzzleNumberCluesImage()
        
    def setPuzzleNumberCluesImage(self):
        number = 0
        pageURL = getPageURL(self.pageDate)
        self.pageURL = getCrosswordURL(pageURL, 'puzzle')
        logging.debug('Crossword Page URL %s' % self.pageURL)
        if self.pageURL is None:
            self.puzzleNumber = number
            return
        logging.debug('Retrieving puzzle from the URL %s' % self.pageURL)
        pageHtml = getResponseString(self.pageURL)
        logging.debug('Puzzle HTML received, searching for Crossword Number')
        numPattern = re.search(r'The\s\s?Hindu\s\s?Crossword.*?[0-9]{2,5}', pageHtml)
        if numPattern is not None:
            number = int(numPattern.group(0).split(' ')[-1])
            logging.debug('Puzzle Number found - Crossword Number %d' %(number))
        self.puzzleNumber = number
        solnNumPattern = numPattern = re.search(r'Solution\s?to\s?puzzle.*?[0-9]{2,5}', pageHtml)
        if solnNumPattern is not None:
            solNumber = int(solNumPattern.group(0).split(' ')[-1])
            logging.debug('Solution Number found - Crossword Number %d' %(solNumber))
        self.solutionNumber = solNumber
        logging.debug('Searching for Images')
        self.pageImages = getImageURLs(puzzleHtml)
        logging.debug('Images found on the page are %s' %('\n'.join (self.pageImages)))
        self.clues = getCluesFromHTML(puzzleHtml)
        logging.debug('Clue search completed!')
        
    def as_str(self, indent=''):
        out = []
        msg = 'Date %s' 
        out.append(indent + msg % (self.pageDate))
        msg = 'Page URL %s' 
        out.append(indent + msg % (self.pageURL))
        msg = 'The Hindu Crossword No. %s' % ( str(self.puzzleNumber))
        out.append(indent + msg)
        msg = 'Solution to puzzle %s' % ( str(self.solutionNumber))
        out.append(indent + msg)
        if len(self.pageImages) > 0:
            for idx, imgURL in self.pageImages:
                msg = ' Candidate Images %d : %s' %idx 
                out.append(indent + msg % (idx+1, self.puzzleImage))
        if self.clues is not None:
            out.append("")
            msg = 'Clues \n%s'
            out.append(indent + msg %('\n'.join(self.clues)))
        return '\n'.join(out)

    def __str__(self):
        return self.as_str()
    

if __name__ == '__main__':
    import timeit
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)-26s %(levelname)-8s %(message)s')
#     startDate = date.today()
    startDate = date(2015,7,3)
#     print startDate
    for day in (startDate - timedelta(n) for n in range(1)):
        try:
            starttime = datetime.now()
            I = ArtifactScraper(day)
            print I
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
     
