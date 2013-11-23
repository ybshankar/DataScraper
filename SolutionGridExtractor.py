from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter, ImageChops
from pytesser import *
from urllib import urlretrieve


def trimBorders(image):
    x,y = image.size
    borderPixel = max(image.getpixel((0,0)),image.getpixel((x-1,y-1)))
    bg = Image.new(image.mode, image.size, borderPixel)
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)

def parseSolutionImage(solutionImage):
    solutionString = ''
    processedImage = trimBorders(solutionImage)
    x,y = processedImage.size
    squareSize = int(5*x/15)
    processedImage = processedImage.resize((int(x*5), int(y*5)), Image.BICUBIC)
    #processedImage = ImageEnhance.Contrast(processedImage)
    processedImage = processedImage.convert("RGBA")
    pix = processedImage.load()
    
    for y in xrange(processedImage.size[1]):
        for x in xrange(processedImage.size[0]):
            borderPixel = ((x % squareSize) < 15) or \
                          ((x % squareSize) > (squareSize - 15)) or \
                          ((y % squareSize) < 15) or \
                          ((y % squareSize) > (squareSize - 15))
            if borderPixel:
                pix[x, y] = (255, 255, 255, 255)
            elif pix[x, y] <=  (30, 30, 30, 255):
                pix[x, y] = (0, 0, 0, 255)
            else:
                pix[x, y] = (255, 255, 255, 255)
    
    #processedImage = processedImage.convert()
    processedImage = processedImage.convert('L')
    processedImage = processedImage.resize((x, y), Image.NEAREST)
    
    filteredImage = filterAndReturnImage(processedImage, minFilter=9, maxFilter=0, blur=True)
    filteredImage.show("30% more contrast")
    solutionString = "Filters : minFilter=9, maxFilter=0, blur=True \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) +'\n\n'

    filteredImage = filterAndReturnImage(processedImage, minFilter=9, maxFilter=0, blur=False)
    filteredImage.show("30% more contrast")
    solutionString = solutionString +  "Filters : minFilter=9, maxFilter=0, blur=False \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) +'\n\n'
    
    filteredImage = filterAndReturnImage(processedImage, minFilter=7, maxFilter=0, blur=True)
    filteredImage.show("30% more contrast")
    solutionString = solutionString + "Filters : minFilter=7, maxFilter=0, blur=True \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) + '\n\n'

    filteredImage = filterAndReturnImage(processedImage, minFilter=7, maxFilter=0, blur=False)
    filteredImage.show("30% more contrast")
    solutionString = solutionString + "Filters : minFilter=7, maxFilter=0, blur=False \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) + '\n\n'
    
    filteredImage = filterAndReturnImage(processedImage, minFilter=11, maxFilter=0, blur=True)
    filteredImage.show("30% more contrast")
    solutionString = solutionString + "Filters : minFilter=11, maxFilter=0, blur=True \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) + '\n\n'
    
    filteredImage = filterAndReturnImage(processedImage, minFilter=11, maxFilter=0, blur=False)
    filteredImage.show("30% more contrast")
    solutionString = solutionString + "Filters : minFilter=11, maxFilter=0, blur=False \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) + '\n\n'

    return solutionString

def filterAndReturnImage(inImage,minFilter=9, maxFilter=0, blur=True):
    if minFilter > 0:
        outImage = inImage.filter(ImageFilter.MinFilter(minFilter))
        
    if maxFilter > 0:
        outImage = inImage.filter(ImageFilter.MaxFilter(maxFilter))
    
    if blur:
        outImage = outImage.filter(ImageFilter.BLUR)
        
    return outImage

def parsePuzzleImage(puzzleImage):
    puzzleString = ""
    processedImage = trimBorders(puzzleImage)
    x,y = processedImage.size
    numCells = 15
    cellSize = int(5*x/numCells)

    processedImage = processedImage.resize((int(x*5), int(y*5)), Image.BICUBIC)
    processedImage = processedImage.convert("RGBA")
    
    processedImage = processedImage.filter(ImageFilter.BLUR)
    pix = processedImage.load()
    
    for y in xrange(processedImage.size[1]):
        for x in xrange(processedImage.size[0]):
            if pix[x, y] <=  (230, 230, 230, 255):
                pix[x, y] = (0, 0, 0, 255)
            else:
                pix[x, y] = (255, 255, 255, 255)
    
    processedImage = processedImage.convert('L')
    processedImage = processedImage.resize((x, y), Image.NEAREST)
    filteredImage = processedImage
    #filteredImage = filterAndReturnImage(processedImage, minFilter=15, maxFilter=3, blur=True)

    #filteredImage = processedImage.filter(ImageFilter.MaxFilter(15))
    #filteredImage = filteredImage.filter(ImageFilter.MinFilter(7))
    #filteredImage = filteredImage.filter(ImageFilter.ModeFilter(21))
    #filteredImage.show("30% more contrast")
    
    for cellY in xrange(numCells):
        puzzleString = puzzleString + "\n"
        for cellX in xrange(numCells):
            startX = int(cellX*cellSize)
            startY = int(cellY*cellSize)
            box = (startX, startY , startX + cellSize, startY+cellSize)
            cellImage = filteredImage.crop(box)
            #cellImage.show("")
            colors = cellImage.getcolors()
            pixels = cellImage.size[0]*cellImage.size[1]
            
            for color in colors:
                if color[0]> int(pixels/2):
                    dominantColor = color
                    break

            if dominantColor[1] == 0:
                cellColor = 'X'
            elif dominantColor[1] == 255:
                cellColor = '_'

            puzzleString = puzzleString + cellColor

    return puzzleString

def displayPuzzleString(puzzleStr):
    displayPuzzleStr = puzzleStr.replace('X', ' X ')
    displayPuzzleStr = displayPuzzleStr.replace('_', ' __')
    return displayPuzzleStr


def enhancedPuzzleString(puzzleStr):
    
    puzzleGrid = puzzleStr.split('\n')
    puzzleGrid = [x for x in puzzleGrid if x not in ['\n', '']]
    enhPuzzleGrid = ["" for x in xrange(len(puzzleGrid))]
    clueCount = 1
    for i in xrange(len(puzzleGrid)):
        for j in xrange(len(puzzleGrid[0])):
            if puzzleGrid[i][j] == "X":
                enhPuzzleGrid[i] = enhPuzzleGrid[i] + " X "
            else:
                neighbours = {'North' : False, 
                              'South' : False, 
                              'East' : False,
                              'West' : False}
                
                if (i == 0): 
                    neighbours['North'] =  True
                    if (puzzleGrid[i+1][j] == "X"):
                        neighbours['South'] = True
                elif (i==(len(puzzleGrid)-1)): 
                    neighbours['South'] =  True
                    if (puzzleGrid[i-1][j] == "X"):
                        neighbours['North'] = True
                else:
                    if (puzzleGrid[i-1][j] == "X"):
                        neighbours['North'] =  True
                    if (puzzleGrid[i+1][j] == "X"):
                        neighbours['South'] =  True
                
                if (j == 0): 
                    neighbours['East'] =  True
                    if (puzzleGrid[i][j+1] == "X"):
                        neighbours['West'] =  True
                elif (j==(len(puzzleGrid)-1)): 
                    neighbours['West'] =  True
                    if (puzzleGrid[i][j-1] == "X"):
                        neighbours['East'] =  True
                else:
                    if (puzzleGrid[i][j-1] == "X"):
                        neighbours['East'] =  True
                    if (puzzleGrid[i][j+1] == "X"):
                        neighbours['West'] =  True
                
                northAndSouthAreSame = (neighbours['North'] and neighbours['South']) or \
                                      ((not neighbours['North']) and (not neighbours['South']))
                
                eastAndWestAreSame = (neighbours['East'] and neighbours['West']) or \
                                      ((not neighbours['East']) and (not neighbours['West']))
                                      
                newClue = False
                
                if  northAndSouthAreSame:
                    if neighbours['East'] and (not neighbours['West']):
                        newClue = True
                elif eastAndWestAreSame:
                    if neighbours['North'] and (not neighbours['South']):
                        newClue = True
                else:
                    if not (neighbours['South'] and neighbours['West']):
                        newClue=True
                
                if newClue:
                    if clueCount <= 9:
                        enhPuzzleGrid[i] = enhPuzzleGrid[i] + str(clueCount) + "__"
                    else:
                        enhPuzzleGrid[i] = enhPuzzleGrid[i] + str(clueCount) + "_"
                    clueCount = clueCount+1
                else:
                    enhPuzzleGrid[i] = enhPuzzleGrid[i] + " __"

    enhPuzzleGrid = "\n".join(enhPuzzleGrid)
    return enhPuzzleGrid

    

def test_solutionParsing(puzzleNum=10875):
     solution = Image.open("puzzles/solution/"+ str(puzzleNum)+".jpg")
     print parseSolutionImage(solution)

def test_puzzleParsing(puzzleNum=10875):
    puzzle = Image.open("puzzles/puzzle/"+ str(puzzleNum)+".jpg")
    puzzleStr = parsePuzzleImage(puzzle)
    print puzzleStr
    print displayPuzzleString(puzzleStr)
    print ""
    print enhancedPuzzleString(puzzleStr)

if  __name__ =='__main__':
    test_puzzleParsing()
#    puzzleNum = 10875
#     solution = Image.open("puzzles/solution/"+ str(puzzleNum)+".jpg")
#     print parseSolutionImage(solution)

#    puzzle = Image.open("puzzles/puzzle/"+ str(puzzleNum)+".jpg")
#    print parsePuzzleImage(puzzle)
# def get(link):
#     urlretrieve(link,'16TH_CROSS_SOL__12_1616119g.jpg')
 
#get('http://www.thehindu.com/todays-paper/tp-miscellaneous/the-hindu-crossword-10902/article5227342.ece');

# puzzle_num = 10875
# puzzle = Image.open("puzzles/puzzle/"+ str(puzzle_num)+".jpg")
# solution = Image.open("puzzles/solution/"+ str(puzzle_num)+".jpg")
# solution=trim(solution)
# puzzle=trim(puzzle)
# s_x,s_y = solution.size
# #box = (3,3, int(10*s_x/15), int(s_y/15))
# #im=solution.crop(box)
# 
# sq_sz = int(5*(s_x)/15)
# im=solution
# nx, ny = im.size
# 
# 
# im2 = im.resize((int(nx*5), int(ny*5)), Image.BICUBIC)
# im2.save("temp2.png")
# enh = ImageEnhance.Contrast(im)
# enh.enhance(1.3).show("30% more contrast")
#  
# imgx = Image.open('temp2.png')
# imgx = imgx.convert("RGBA")
# pix = imgx.load()
# 
# for y in xrange(imgx.size[1]):
#     for x in xrange(imgx.size[0]):
# 
#         borderPixel = ((x % sq_sz) < 15) or ((x % sq_sz) > (sq_sz - 15)) or \
#                       ((y % sq_sz) < 15) or ((y % sq_sz) > (sq_sz - 15))
# 
#         if borderPixel:
#             pix[x, y] = (255, 255, 255, 255)
#             continue
# 
#         if pix[x, y] <=  (30, 30, 30, 255):
#             pix[x, y] = (0, 0, 0, 255)
#         else:
#             pix[x, y] = (255, 255, 255, 255)
# imgx=imgx.filter(ImageFilter.MinFilter(9))
# #imgx=imgx.filter(ImageFilter.MaxFilter(5))
# imgx=imgx.filter(ImageFilter.BLUR)
# imgx.save("bw.gif", "GIF")
# imgx.show("30% more contrast")
# original = Image.open('bw.gif')
# bg = original.resize((int(nx), int(ny)), Image.NEAREST)
# ext = ".tif"
# bg.save("input-NEAREST" + ext)
# image = Image.open('input-NEAREST.tif')
# print image_to_string(image)
