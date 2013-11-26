'''
Created on Nov 25, 2013

@author: byanamadala
'''
from datetime import *

import urllib2
import re

def getResponseString(URL):
    htmlStr = None
    try:
        response = urllib2.urlopen(URL)
        htmlStr = response.read()
    except Exception as e:
        print 'exception reaching URL %s %s %s' (URL,e.value, e.strerror)
        print sys.exc_info()
    return htmlStr

class ImageScraper(object):
    puzzle = None
    solution = None
    clues = None
    puzzleDate = None
    solutionDate = None

    def __init__(self, puzzleDate=date.today(), solutionDate=None):
        '''
        
        '''
        self.puzzleDate = puzzleDate
        self.solutionDate = solutionDate
        
        if solutionDate is None:
            self._setSolutionDateIfExists()


        
    def _setSolutionDateIfExists(self):
        if self.solutionDate is not None:
            return
        weekday = self.puzzleDate.weekday()
        if weekday == 6:
            self.solutionDate = self.puzzleDate + timedelta(days=7)
        elif weekday == 5:
            self.solutionDate = self.puzzleDate + timedelta(days=2)
        else:
            self.solutionDate = self.puzzleDate + timedelta(days=1)
        
    def getPageURL(self,urltype='puzzle'):
        if urltype == 'puzzle':
            primaryDate= self.puzzleDate
        else:
            primaryDate = self.solutionDate
        
        if primaryDate > date(2006,1,1):
            fullURL = r'http://www.thehindu.com/archive/print/'+ primaryDate.strftime(r'%Y/%m/%d/') +r'#miscelaneous'
        else:
            fullURL = r'http://www.hindu.com/thehindu/'+ primaryDate.strftime(r'%Y/%m/%d/')+'10hdline.htm'
        return fullURL
    
    def getCrosswordURL(self, urltype='puzzle'):
        pageURL = self.getPageURL(urltype)
        htmlStr = getResponseString(pageURL)
        if htmlStr is None:
            return None

        xWordURL = re.search(r'<a.*?>The Hindu Crossword .*?</a>', htmlStr)
        
        if xWordURL is None:
            return None

        xWordURL = xWordURL.group(0).split('"')[1]
        xWordURLList = pageURL.split('/')[:-1]
        
        if not xWordURL.startswith('http'):
            xWordURLList.append(xWordURL)
            xWordURL='/'.join(xWordURLList)
        
        oldXWordSolURL = re.search(r'<a.*?>Solution to Puzzle .*?</a>', htmlStr)
        if oldXWordSolURL is not None:
            oldXWordSolURL=oldXWordSolURL.group(0).split('"')[1]
            xWordURLList.append(oldXWordSolURL)
            oldXWordSolURL='/'.join(xWordURLList)
        
        newXWordSolURL = re.search(r'<a.*?>Solution No .*?</a>', htmlStr)
        if newXWordSolURL is not None:
            newXWordSolURL=newXWordSolURL.group(0).split('"')[1]
        
        if urltype != 'puzzle':
            if oldXWordSolURL is not None:
                return oldXWordSolURL
            elif newXWordSolURL is not None:
                return newXwordSolURL

        return xWordURL

        
        

            
    
#    def getPuzzleImage(self):
        
        
    
#    def getSolutionImage(self):



    def __str__(self):
        return ""

if __name__ == '__main__':
#     print ImageScraper(date(2013,5,19)).getCrosswordURL('puzzle')
#     print ImageScraper(date(2013,5,19)).getCrosswordURL('solution')
#     
#     print ImageScraper(date(2003,5,19)).getCrosswordURL('puzzle')
#     print ImageScraper(date(2003,5,19)).getCrosswordURL('solution')
#     
#     print ImageScraper(date(2006,1,1)).getCrosswordURL('puzzle')
    print ImageScraper(date(2006,1,1)).getCrosswordURL('solution')
