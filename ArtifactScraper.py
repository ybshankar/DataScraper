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
from collections import OrderedDict
from json import loads, dumps

def loadYamlFile(filename):
    with open(filename, 'r') as cf:
        yamlDoc = yaml.load(cf)
    return yamlDoc

def writeYamlDocToFile(yamlDoc, filename):
    with open(filename, 'wb') as cf:
        cf.write(yaml.dump(yamlDoc))

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
    
def getCrosswordURL(pageURL, htmlStr):
    logging.debug('Received HTML Response, searching for patterns')
    if htmlStr is None:
        return None
    
    xWordURLList = pageURL.split('/')[:-1]
    solnURL = None

    xWordURL = re.search(r'<a.*?>.*?\s?\s?Hindu\s?\s?Crossword\s?\s?.*?</a>', htmlStr, flags=re.IGNORECASE)
    oldXWordSolURL = re.search(r'<a.*?>Solution\s?\s?to\s?\s?Puzzle.*?</a>', htmlStr, flags=re.IGNORECASE)
    newXWordSolURL = re.search(r'<a.*?>Solution No.*?</a>', htmlStr, flags=re.IGNORECASE)
        
    if xWordURL is None:
        xWordURL = re.search(r'<a.*?>.*guardian.*crossword\s?\s?.*?</a>', htmlStr, flags=re.IGNORECASE)
        if xWordURL is None:
            return None
    
    if xWordURL is not None:
        xWordURL = xWordURL.group(0).split('"')[-2]
        if not xWordURL.startswith('http'):
            xWordURLList.append(xWordURL)
            xWordURL='/'.join(xWordURLList)
        logging.debug('Puzzle Pattern found: %s' %(xWordURL))

        
    if oldXWordSolURL is not None:
        logging.debug('Puzzle Pattern found: %s' %(xWordURL))
        oldXWordSolURL=oldXWordSolURL.group(0).split('"')[1]
        if not oldXWordSolURL.startswith('http'):
            xWordURLList.append(oldXWordSolURL)
            solnURL='/'.join(xWordURLList)
        else:
            solnURL = oldXWordSolURL
    elif newXWordSolURL is not None:
        solnURL=newXWordSolURL.group(0).split('"')[1]

    logging.debug('Solution Pattern found: %s' %(solnURL))
    return xWordURL, solnURL


def getImageURLs(htmlString):
    #### TODO
    # needs to work with patterns found in page http://www.thehindu.com/todays-paper/tp-miscellaneous/the-hindu-crossword-11436/article7373825.ece
    # use the carousel div to identify the image rather than using the cross word string.
#     imgPatterns = re.finditer(r'<img src="http://www.thehindu.com/multimedia/dynamic/.*?CROSS.*?.jpg\s?" height="400".*?"/>', htmlString, flags=re.IGNORECASE)
    if r'''<div class="jcarousel-wrapper">''' in htmlString:
        splitString = htmlString.split(r'''<div class="jcarousel-wrapper">''')[1]
        splitString = splitString.split(r'''<script type="text/javascript">''')[0]
    elif r'''<div id="left-column">''' in htmlString:
        splitString = htmlString.split(r'''<div id="left-column">''')[1]
        splitString = splitString.split(r'''<div id="right-column">''')[0]
    else:
        splitString = htmlString
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
    
    return  clues


class ArtifactScraper(object):
    pageDate = None
    miscPageURL = None
    pageURL = None
    solnURL = None
    puzzleNumber = None
    solutionNumber = None
    rawClues = []
    pageImages = []

    def __init__(self, pageDate=date.today()):
        '''
        
        '''
        self.pageDate = pageDate
        self.setPuzzleNumberCluesImage()
        
    def setPuzzleNumberCluesImage(self):
        number = 0
        solNumber=0
        self.miscPageURL = getPageURL(self.pageDate)
        logging.debug('Getting URL for puzzle at %s' %(self.miscPageURL))
        miscHtmlStr = getResponseString(self.miscPageURL)
        self.pageURL, self.solnURL = getCrosswordURL(self.miscPageURL, miscHtmlStr)
        if self.pageURL is None:
            raise Exception("Unable to detect crossword page URL\n")
        else:
            logging.debug('Crossword Page URL %s' % self.pageURL)
        logging.debug('Retrieving puzzle from the URL %s' % self.pageURL)
        pageHtml = getResponseString(self.pageURL)
        pageImages = getImageURLs(miscHtmlStr)
#         pageImages = []
        
        logging.debug('Puzzle HTML received, searching for Crossword Number')
        if 'guardian' in self.pageURL.lower():
            numPattern = re.search(r'The\s\s?guardian\s\s?quick\s\s?Crossword.*?[0-9]{2,5}', pageHtml)
        else:
            numPattern = re.search(r'The\s\s?Hindu\s\s?Crossword.*?[0-9]{2,5}', pageHtml)
        if numPattern is not None:
            number = int(numPattern.group(0).split(' ')[-1].replace('.', '').replace('No', ''))
            logging.debug('Puzzle Number found - Crossword Number %d' %(number))
        self.puzzleNumber = number
        solHtml=''
        if not self.solnURL:
            solHTML = pageHtml
            solImages = []
        else:
            solHtml = getResponseString(self.solnURL)
            solImages = getImageURLs(solHtml)
            
        solNumPattern = re.search(r'Solution\s?to\s?puzzle.*?[0-9]{2,5}', solHtml)
        if solNumPattern is not None:
            solNumber = int(solNumPattern.group(0).split(' ')[-1])
            logging.debug('Solution Number found - Crossword Number %d' %(solNumber))
        self.solutionNumber = solNumber


        if (self.puzzleNumber != 0) and (self.solutionNumber==0):
            self.solutionNumber = self.puzzleNumber - 1
            logging.debug ('Solution Number not found, guessing it based on puzzle number, solution number %d' % self.solutionNumber)

        logging.debug('Searching for Images')
        crosswordPageImages= getImageURLs(pageHtml)
        self.pageImages = [ x for x in crosswordPageImages if x not in pageImages]
        self.pageImages.extend([ x for x in solImages if x not in pageImages])
        logging.debug('Images found on the page are %s' %('\n'.join (self.pageImages)))
        self.rawClues= getCluesFromHTML(pageHtml)
        logging.debug('Clue search completed!')
    
    def getYamlDict(self):

        yamlDict = {}
        yamlDict[str(self.pageDate)]={'puzzleNumber':self.puzzleNumber,
                                      'miscPageURL': self.miscPageURL, 
                                      'pageURL': self.pageURL, 
                                 'solutionNumber':self.solutionNumber,
                                 'Images': self.pageImages, 
                                 'rawClues': self.rawClues}
        return yamlDict
        
    def as_str(self, indent=''):
        out = []
        msg = 'Date %s' 
        out.append(indent + msg % (self.pageDate))
        msg = 'Archive Page URL %s' 
        out.append(indent + msg % (self.miscPageURL))
        msg = 'Page URL %s' 
        out.append(indent + msg % (self.pageURL))
        msg = 'The Hindu Crossword No. %s' % ( str(self.puzzleNumber))
        out.append(indent + msg)
        msg = 'Solution to puzzle %s' % ( str(self.solutionNumber))
        out.append(indent + msg)
        if len(self.pageImages) > 0:
            for idx, imgURL in enumerate(self.pageImages):
                msg = 'Candidate Images %d : %s' 
                out.append(indent + msg % (idx+1, imgURL))
        if self.rawClues is not None:
            out.append("")
            msg = 'Clues \n%s'
#             out.append(indent + msg)
            out.append(indent + msg %('\n'.join(self.rawClues)))
        return '\n'.join(out)

    def __str__(self):
        return self.as_str()
    

if __name__ == '__main__':
    excludedDatesList=['2015-07-12','2015-06-14', '2015-04-12', '2015-01-16', 
                       '2014-11-17', '2014-10-23', '2014-10-04',
                       '2014-10-03', '2014-09-30', '2014-06-18',
                       '2014-06-17', '2014-03-30', '2014-02-09',
                       '2014-02-02', '2014-01-26', '2014-01-19',
                       '2014-01-15', '2014-01-12', '2013-12-22', 
                       '2013-11-10', '2013-02-24', '2013-02-17',
                       '2013-02-10', '2013-02-03', '2013-01-27',
                       '2013-01-20', '2013-01-13', '2013-01-06',
                       '2012-12-30', '2012-12-23', '2012-12-16',
                       '2012-12-09', '2012-12-02', '2012-11-25',
                       '2012-11-18', '2012-11-11', '2012-11-04',
                       '2012-10-28', '2012-10-21', '2012-10-14',
                       '2012-10-07', '2012-09-30', '2012-09-23',
                       '2012-09-16']
    import timeit
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)-26s %(levelname)-8s %(message)s')
    
    hdlr = logging.FileHandler(os.path.abspath(os.path.join(__file__, '..', 'puzzles', 'pageData.log')))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(hdlr) 
#     startDate = date.today()
    startDate = date(2010, 6, 3)
    filename = os.path.abspath(os.path.join(__file__, '..', 'puzzles', 'pageData.yaml'))
    try:
        yamlDict = loadYamlFile(filename)
    except:
        yamlDict = None
    finally:
        if yamlDict == None:
            yamlDict = {}
#     yamlDict={}
#     yamlDict = OrderedDict(sorted(yamlDict.items(), key=lambda x:x[1], reverse=True))
#     print startDate
    for day in (startDate - timedelta(n) for n in range(4000)):
        processXword = False
        if (str(day) in excludedDatesList):
            continue
        elif (str(day) in yamlDict.keys()):
            if len(yamlDict[str(day)]['Images']) != 0:
                continue
            else:
                processXword = True
        else:
            processXword = True

        if processXword:
            try:
                starttime = datetime.now()
                 
                I = ArtifactScraper(day)
                print I
                yamlDict.update(I.getYamlDict())
                writeYamlDocToFile(yamlDict, filename)
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
     
