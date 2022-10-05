#written for raspberry pi and uses the Adafruit_NeoPixel library
import time
from rpi_ws281x import *
import pygame
import os
#----------------------------------------------------------------------------------------
dir         = os.path.dirname(os.path.realpath(__file__))
mode        = 0
rows        = 0
cols        = 0
scrMode     = 0
preFrame    = 0
postFrame   = 0
frameCnt    = 0
patternName = ""
frameCnt    = 0
gpio        = 18
freqhz      = 800000
dma         = 10
bright      = 10
inv         = 0
spd         = 0.0167
gapColor    = "#000000 "
#----------------------------------------------------------------------------------------
#reading config file
try:
    config = open(dir + "/config.cfg", "r")
    cnt = 0;
    
    for ln in config:
        if ln[0] != '!':
        
            if "mode = " in ln:
                mode = int(ln[7:])
            
            elif "rows = " in ln:
                rows = int(ln[7:])
            
            elif "columns = " in ln:
                cols = int(ln[10:])
            
            elif "scrollMode = " in ln:
                scrMode = int(ln[13:])
            
            elif "preFrame = " in ln:
                preFrame = float(ln[11:])
            
            elif "postFrame = " in ln:
                postFrame = float(ln[12:])
            
            elif "patternFile = " in ln:
                patternName = ln[14:]
                patternName = patternName[:len(patternName) - 2]
            
            elif "frames = " in ln:
                frameCnt = int(ln[9:])
            
            elif "gpio = " in ln:    
                gpio = int(ln[7:])
            
            elif "freqhz = " in ln:
                freqhz = int(ln[9:])
                freqhz = freqhz * 1000
            
            elif "dma = " in ln:
                dma = int(ln[6:])
            
            elif "brightness = " in ln:
                bright = int(ln[13:])
            
            elif "inv = " in ln:
                inv = int(ln[6:])
            
            elif "speed = " in ln:
                spd = spd/float(ln[8:])
            
            elif "gapColor = " in ln:
                gapColor = ln[11:]

    config.close()
except:
    print("missing config")
    exit()
#----------------------------------------------------------------------------------------
#setting up physical matrix config
LED_COUNT       = rows * cols
LED_PIN         = gpio
LED_FREQ_HZ     = freqhz
LED_DMA         = dma
LED_BRIGHTNESS  = bright
LED_INVERT      = False
LED_CHANNEL     = 0

if inv == 1:
    LED_INVERT  = True

if gpio == 13 or gpio == 19 or gpio == 41 or gpio == 45 or gpio == 53:
    LED_CHANNEL = 1

matrixStrip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
matrixStrip.begin()
#----------------------------------------------------------------------------------------
#setting up a virtual matrix (meant for a zig-zag LED matrix)
pixelMatrix     = [[None for y in range(rows)] for x in range(cols)]
flip            = False
pixelCnt        = 0
x               = 0
y               = 0
a               = rows - 1

while x < cols:
    while y < rows:
        if not flip:
            pixelMatrix[x][y] = pixelCnt
            a = rows - 1
        elif flip:
            pixelMatrix[x][y] = pixelCnt + a
            a -= 2
        
        y           += 1
        pixelCnt    += 1
        
    flip    = not flip
    x      += 1
    y       = 0
#----------------------------------------------------------------------------------------
#reading pattern file
pattern = None

if mode == 0:
    pattern = [None for i in range(rows * cols)]
elif mode == 1:
    pattern = []
elif mode == 2:
    pattern = []

try:
    patternFile = open(dir + "/" + patternName, "r")
    i = 0
    
    #mode 0 loads a list of colors, where the length is the product of rows and cols
    if mode == 0:
        
        for hexColor in patternFile:
            
            if hexColor[0] == '#':
                pattern[i] = pygame.Color(hexColor[:7])
                i += 1
    
    #mode 1 loads a list of color lists, where each color list contains a row of hex colors
    elif mode == 1:
        
        if scrMode > 1:
            pattern.append([pygame.Color(gapColor[:7]) for a in range(cols)])
        
        tmp = []
        for hexColor in patternFile:
            
            if hexColor[0] == '#':
                if i == 0 and scrMode < 2:
                    tmp.append(pygame.Color(gapColor[:7]))
                    
                tmp.append(pygame.Color(hexColor[:7]))
                i += 1
            
            elif hexColor[0] == '-':
                if scrMode < 2:
                    tmp.append(pygame.Color(gapColor[:7]))
                
                pattern.append(tmp)
                i = 0
                tmp = []
        
        if scrMode > 1:
            for b in range(rows):
                pattern.append([pygame.Color(gapColor[:7]) for a in range(cols)]) 
    
    #mode 2 loads a list of color lists, where the length of each color list is the product of rows and cols
    elif mode == 2:
    
        tmp = [None for x in range(rows * cols)]
        for hexColor in patternFile:
            
            if hexColor[0] == '#':
                tmp[i] = pygame.Color(hexColor[:7])
                i += 1
                
            elif hexColor[0] == '=':
                pattern.append(tmp)
                i = 0
                tmp = [None for x in range(rows * cols)]
    
    patternFile.close()
    
except:
    print("missing pattern")
    exit()
#----------------------------------------------------------------------------------------
def clearColor():
    x = 0
    y = 0
    
    while y < rows:
        while x < cols:
            matrixStrip.setPixelColor(pixelMatrix[x][y], Color(0, 0, 0))
            x += 1
        y += 1
        x = 0
    matrixStrip.show()
#----------------------------------------------------------------------------------------
def staticPattern():
    x = 0
    y = 0
    i = 0
    
    while y < rows:
        while x < cols:
            matrixStrip.setPixelColor(pixelMatrix[x][y], Color(pattern[i].r, pattern[i].g, pattern[i].b))
            i += 1
            x += 1
        y += 1
        x = 0

    matrixStrip.show()
    time.sleep(60)
#----------------------------------------------------------------------------------------
def scrollPattern():
    
    if scrMode == 0:
        x       = cols - 1          #sets the position we'll be scrolling from; x = cols - 1 since we'll be going from right to left 
        y       = 0                 #sets the y position we start from, which will be 0 in this mode
        z       = len(pattern[0])   #the number of columns we'll be scrolling through. since we're scrolling, it might be larger than x
        mini    = 0                 #sets the minimum number of pattern pixels being displayed in a given iteration
        maxi    = 1                 #sets the maximum number of pattern pixels that can be displayed in a given iteration
        
        #loops while x is greater than -z. this doubles z space and gives enough space for the entire pattern to be scrolled
        while x > -z:   #loops the process until x surpasses the alloted space provided by -z, allowing the entire pattern to be scrolled
            for colorList in pattern:
                while mini < maxi:      #loops the current row until the minimum reaches the maximum. this gives the scrolling effect
                    if mini < z and ( -1 < (x + mini) < cols ):     #outputs pixel x and whatever pixels appear after x (if applicable)
                        matrixStrip.setPixelColor(pixelMatrix[x + mini][y], Color(colorList[mini].r, colorList[mini].g, colorList[mini].b))    #scrolling from right to left, hence x + mini
                    
                    mini += 1
                
                y += 1
                mini = 0
            
            matrixStrip.show()
            time.sleep(spd)
            
            
            x      -= 1 #subtracts from x since we scroll to the left 
            y       = 0
            mini    = 0
            maxi   += 1 #increases the maximum number of pixels from the pattern we can display
                        
        time.sleep(postFrame)
    #----------------------------------------------------------------------------------------
    elif scrMode == 1:  #same process as mode 1, but certain values are swapped to yield the same effect in the opposite direction 
        x       = 0
        y       = 0
        z       = len(pattern[0]) - 1
        mini    = 0
        maxi    = 1
        
        while x < z*2:
            for colorList in pattern:
                while mini < maxi:
                    if mini < z + 1 and ( -1 < (x - mini) < cols ):
                        matrixStrip.setPixelColor(pixelMatrix[x - mini][y], Color(colorList[z - mini].r, colorList[z - mini].g, colorList[z - mini].b))
                    
                    mini += 1
                
                y += 1
                mini = 0
            
            matrixStrip.show()
            time.sleep(spd)
            
            x      += 1
            y       = 0
            mini    = 0
            maxi   += 1
            
            if x > cols - 1:
                mini = -x
        
        time.sleep(postFrame)        
    #----------------------------------------------------------------------------------------
    elif scrMode == 2:
        x       = 0
        y       = 0
        z       = len(pattern)
        mini    = 0
        maxi    = 1
        
        while y < z*2:
            for row in pattern:
                if mini < maxi and mini < z and ( -1 < (y - mini) < rows ):
                    for col in row:
                        matrixStrip.setPixelColor(pixelMatrix[x][y - mini], Color(col.r, col.g, col.b))
                        x += 1
                    
                mini += 1
                x = 0
            
            matrixStrip.show()
            time.sleep(spd * 2)
            
            x       = 0
            y      += 1
            mini    = 0
            maxi   += 1
        
        time.sleep(postFrame)
    #----------------------------------------------------------------------------------------    
    elif scrMode == 3:
        x       = 0
        y       = rows - 1
        z       = len(pattern)
        mini    = 0
        maxi    = 1
        
        while y > -z:
            for row in pattern:
                if mini < maxi and mini < z and ( -1 < (y + mini) < rows ):
                    for col in row:
                        matrixStrip.setPixelColor(pixelMatrix[x][y + mini], Color(col.r, col.g, col.b))
                        x += 1
                    
                mini += 1
                x = 0
            
            matrixStrip.show()
            time.sleep(spd * 2)
            
            x       = 0
            y      -= 1
            mini    = 0
            maxi   += 1
                
        
        time.sleep(postFrame)
#----------------------------------------------------------------------------------------
def fbfPattern():
    x = 0
    y = 0
    i = 0
    
    for frame in pattern:
        while y < rows:
            while x < cols:
                matrixStrip.setPixelColor(pixelMatrix[x][y], Color(frame[i].r, frame[i].g, frame[i].b))
                i += 1
                x += 1
            y += 1
            x = 0

        matrixStrip.show()
        time.sleep(spd * 2)
        x = 0
        y = 0
        i = 0
#----------------------------------------------------------------------------------------
#loop displaying the pattern
clearColor()
try:
    if mode == 1:
        if gapColor != "#000000":
            x = 0
            y = 0
            i = pygame.Color(gapColor[:7])
    
            while y < rows:
                while x < cols:
                    matrixStrip.setPixelColor(pixelMatrix[x][y], Color(i.r, i.g, i.b))
                    x += 1
                y += 1
                x = 0
            
            matrixStrip.show()

    while True:
        time.sleep(preFrame)
        if mode == 0:
            staticPattern()
        elif mode == 1:
            scrollPattern()
        elif mode == 2:
            fbfPattern()
            
except KeyboardInterrupt:
    clearColor()
    exit()
#----------------------------------------------------------------------------------------