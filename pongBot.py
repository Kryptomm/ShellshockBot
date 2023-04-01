from PIL import ImageGrab
from time import time

import queue, numpy

#Coordinates
regTopLeft = (672, 312)
regBottomRight = (1246, 695)
region = (regTopLeft[0], regTopLeft[1], regBottomRight[0], regBottomRight[1])

topLeft = (0,0)
bottomRight = (regBottomRight[0] - regTopLeft[0], regBottomRight[1] - regTopLeft[1])

numberRegions = [(817,327,833,352),(1086,327,1102,352)]
#Colors
BallColors = [(255,255,255),(228,229,230)]

def getBallTrajectory(image, lastBallCoordinate, pixelDistance):
    m, b = 0, 0
    firstColorFound, secondColorFound = False, False

    pixelQueue = queue.Queue()
    pixelQueue.put(lastBallCoordinate)
    
    visited = numpy.zeros((bottomRight[0],bottomRight[1]), dtype=bool)
    visited[lastBallCoordinate[0]][lastBallCoordinate[1]] = True
    
    firstColorPosition, secondColorPosition = (), ()
    
    while not pixelQueue.empty():
        currentPixel = pixelQueue.get()
        colors = image.getpixel(currentPixel)
        
        if colors == BallColors[0]:
            firstColorPosition = currentPixel
            firstColorFound = True
            if firstColorFound and secondColorFound: break
            
        elif colors == BallColors[1]:
            secondColorPosition = currentPixel
            secondColorFound = True
            if firstColorFound and secondColorFound: break
        
        if currentPixel[0] + pixelDistance < bottomRight[0] and not visited[currentPixel[0] + pixelDistance][currentPixel[1]]:
            pixelQueue.put((currentPixel[0] + pixelDistance, currentPixel[1]))
            visited[currentPixel[0] + pixelDistance][currentPixel[1]] = True
            
        if currentPixel[0] - pixelDistance > topLeft[0] and not visited[currentPixel[0] - pixelDistance][currentPixel[1]]:
            pixelQueue.put((currentPixel[0] - pixelDistance, currentPixel[1]))
            visited[currentPixel[0] - pixelDistance][currentPixel[1]] = True
            
        if currentPixel[1] + pixelDistance < bottomRight[1] and not visited[currentPixel[0]][currentPixel[1] + pixelDistance]:
            pixelQueue.put((currentPixel[0], currentPixel[1] + pixelDistance))
            visited[currentPixel[0]][currentPixel[1] + pixelDistance] = True
            
        if currentPixel[1] - pixelDistance > topLeft[1] and not visited[currentPixel[0]][currentPixel[1] - pixelDistance]:
            pixelQueue.put((currentPixel[0], currentPixel[1] - pixelDistance))
            visited[currentPixel[0]][currentPixel[1] - pixelDistance] = True
    
    return m, b, firstColorPosition

def main():
    lastBallCoordinate = (0,0)
    lastOwnCoordinate = (0,0)
    
    while True:
        startTime = time()
        
        screenshot = ImageGrab.grab()

        #draw the numbers Black so it wont effect the Ball Searching Algorhitm
        for x in range(numberRegions[0][0], numberRegions[0][2]):
            for y in range(numberRegions[0][1], numberRegions[0][3]):
                screenshot.putpixel((x, y), (0, 0, 0))
                
        for x in range(numberRegions[1][0], numberRegions[1][2]):
            for y in range(numberRegions[1][1], numberRegions[1][3]):
                screenshot.putpixel((x, y), (0, 0, 0))
        
        screenshot = screenshot.crop(region)
                
        endTime = time()
        print(f"Blacking needed {endTime - startTime}s")
        ball_m, ball_b, lastBallCoordinate = getBallTrajectory(screenshot, lastBallCoordinate, 3)
        
        endTime = time()
        print(f"Calculations needed {endTime - startTime}s")


if __name__ == "__main__":
    main()