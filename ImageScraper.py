'''
Created on Nov 25, 2013

@author: byanamadala
'''
from datetime import *
class ImageScraper(object):
    self.puzzle = None
    self.solution = None
    self.clues = None
    self.puzzleDate = date.today()
    self.solutionDate = None

    def __init__(self, puzzleDate):
        '''
        
        '''

        self.puzzleDate = puzzleDate
        
    def doesSolutionExist(self):
        weekday = self.puzzleDate.weekday()
        if weekday == 6:
            self.solutionDate = self.puzzleDate + timedelta(days=7)
        else:
            self.solutionDate = self.puzzleDate + timedelta(days=1)
        return (datetime.today() >= self.solutionDate)



    def __str__(self):
        return ""

if __name__ == '__main__':
    pass