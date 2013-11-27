'''
Created on Nov 25, 2013

@author: byanamadala
'''
from datetime import *

import urllib2
import re
import os, sys

def getResponseString(URL):
    htmlStr = None
    try:
        response = urllib2.urlopen(URL)
        htmlStr = response.read()
    except Exception as e:
        print 'exception reaching URL %s %s %s' %(URL, e.code, e.msg)
        print sys.exc_info()
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
    htmlStr = getResponseString(pageURL)
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

    return xWordURL

class ImageScraper(object):
    puzzle = None
    solution = None
    clues = None
    puzzleDate = None
    number = None
    solutionDate = None
    puzzleURL = None
    solutionURL = None

    def __init__(self, puzzleDate=date.today(), solutionDate=None):
        '''
        
        '''
        self.puzzleDate = puzzleDate
        self.solutionDate = solutionDate
        self.puzzleURL = self.getPuzzleURL()
        self.number = self.setPuzzleNumber()
        self.setSolutionURL()
        
    def getPuzzleURL(self):
        pageURL = getPageURL(self.puzzleDate)
        return getCrosswordURL(pageURL, 'puzzle')


    def setPuzzleNumber(self):
        number = 0
        if self.puzzleURL is not None:
            puzzleHtml = getResponseString(self.puzzleURL)
            numPattern = re.search(r'The\s\s?Hindu\s\s?Crossword.*?[0-9]{2,5}', puzzleHtml)
            if numPattern is not None:
                number = int(numPattern.group(0).split(' ')[-1])
        return number
        
    def setSolutionURL(self):
        solutionDateUndetermined = (self.puzzleURL is not None) and (self.solutionDate is None)
        if solutionDateUndetermined:
            self.solutionDate = getNextSolutionDate(self.puzzleDate)
            for tries in xrange(5):
                if self.solutionDate > date.today():
                    break
                pageURL = getPageURL(self.solutionDate)
                self.solutionURL = getCrosswordURL(pageURL, 'solution', self.number)
                if self.solutionURL is not None:
                    break
                self.solutionDate= getNextSolutionDate(self.solutionDate)

    
#    def getPuzzleImage(self):
    
#    def getSolutionImage(self):

    def as_str(self, indent=''):
        out = []
        msg = 'The Hindu Crossword No. %s' % ( str(self.number))
        out.append(indent + msg)
        msg = 'Puzzle Dated %s' 
        out.append(indent + msg % (self.puzzleDate))
        msg = 'Puzzle URL %s' 
        out.append(indent + msg % (self.puzzleURL))
        if self.solutionURL is not None:
            msg = 'Solution Date %s' 
            out.append(indent + msg % (self.solutionDate))
            msg = 'Solution URL %s' 
            out.append(indent + msg % (self.solutionURL))
                    
        return '\n'.join(out)

    def __str__(self):
        return self.as_str()

if __name__ == '__main__':
     print ImageScraper(date(2013,5,19))
     print 
     print ImageScraper(date(2003,5,19))
     print 
     print ImageScraper(date(2006,1,1))
     
