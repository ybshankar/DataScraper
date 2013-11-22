from PIL import Image
from PIL import ImageEnhance
from pytesser import *
from urllib import urlretrieve
 
# def get(link):
#     urlretrieve(link,'16TH_CROSS_SOL__12_1616119g.jpg')
 
#get('http://www.thehindu.com/todays-paper/tp-miscellaneous/the-hindu-crossword-10902/article5227342.ece');
puzzle = Image.open("puzzle.png")
solution = Image.open("solution.png")
s_x,s_y = solution.size
#box = (3,3, int(10*s_x/15), int(s_y/15))
#im=solution.crop(box)
sq_sz = int(5*(s_x -5)/15)
im=solution
nx, ny = im.size


im2 = im.resize((int(nx*5), int(ny*5)), Image.BICUBIC)
im2.save("temp2.png")
enh = ImageEnhance.Contrast(im)
#enh.enhance(1.3).show("30% more contrast")
 
imgx = Image.open('temp2.png')
imgx = imgx.convert("RGBA")
pix = imgx.load()

for y in xrange(imgx.size[1]):
    for x in xrange(imgx.size[0]):
        borderPixel = ((x % sq_sz) < 15) or ((x % sq_sz) > (sq_sz - 15)) or \
                      ((y % sq_sz) < 15) or ((y % sq_sz) > (sq_sz - 15))

        if borderPixel:
            pix[x, y] = (255, 255, 255, 255)
            continue

        if pix[x, y] <=  (30, 30, 30, 255):
            pix[x, y] = (0, 0, 0, 255)
        else:
            pix[x, y] = (255, 255, 255, 255)

            
imgx.save("bw.gif", "GIF")
imgx.show("30% more contrast")
original = Image.open('bw.gif')
bg = original.resize((int(nx), int(ny)), Image.NEAREST)
ext = ".tif"
bg.save("input-NEAREST" + ext)
image = Image.open('input-NEAREST.tif')
print image_to_string(image)