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
    processedImageImg = processedImage.convert("RGBA")
    pix = processedImageImg.load()
    
    for y in xrange(processedImageImg.size[1]):
        for x in xrange(processedImageImg.size[0]):
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
    processedImage = processedImageImg.convert('L')
    processedImage = processedImage.resize((x, y), Image.NEAREST)
    filteredImage = filterAndReturnImage(processedImage)
    solutionString = "Default filters : (minFilter(7), blur) \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) +'\n\n'
    filteredImage = filterAndReturnImage(processedImage, minFilter=3, maxFilter=3, blur=True)
    solutionString = solutionString + "Filters : (minFilter(3), blur) \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) + '\n\n'
    filteredImage = filterAndReturnImage(processedImage, minFilter=9, maxFilter=0, blur=True)
    solutionString = solutionString + "Filters : (minFilter(5), blur) \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) + '\n\n'
    filteredImage = filterAndReturnImage(processedImage, minFilter=5, maxFilter=9, blur=True)
    solutionString = solutionString + "Filters : (minFilter(9), blur) \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) + '\n\n'
    filteredImage = filterAndReturnImage(processedImage, minFilter=11, maxFilter=21, blur=True)
    solutionString = solutionString + "Filters : (minFilter(21), blur) \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) + '\n\n'
    filteredImage = filterAndReturnImage(processedImage, minFilter=15, maxFilter=7, blur=False)
    solutionString = solutionString + "Filters : (minFilter(7)) \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) +'\n\n'
    filteredImage = filterAndReturnImage(processedImage, minFilter=9, maxFilter=3, blur=False)
    solutionString = solutionString + "Filters : (minFilter(3)) \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) + '\n\n'
    filteredImage = filterAndReturnImage(processedImage, minFilter=3, maxFilter=5, blur=False)
    solutionString = solutionString + "Filters : (minFilter(5)) \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) + '\n\n'
    filteredImage = filterAndReturnImage(processedImage, minFilter=3, maxFilter=9, blur=False)
    solutionString = solutionString + "Filters : (minFilter(9), blur) \n\n"
    solutionString =  solutionString + image_to_string(filteredImage, True) + '\n\n'

    return solutionString




def filterAndReturnImage(inImage,minFilter=9, maxFilter=7, blur=True):
    if minFilter > 0:
        outImage = inImage.filter(ImageFilter.MinFilter(minFilter))
        
    if maxFilter > 0:
        outImage = inImage.filter(ImageFilter.MaxFilter(maxFilter))
    
    if blur:
        outImage = outImage.filter(ImageFilter.BLUR)
        
    return outImage


def createPuzzleString(puzzleImage):
    puzzleString = None
    return puzzleString

if  __name__ =='__main__':
    puzzle_num = 10875
    solution = Image.open("puzzles/solution/"+ str(puzzle_num)+".jpg")
    print parseSolutionImage(solution)
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
