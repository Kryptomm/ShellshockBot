import math
import numpy
import visualizer
from collections import deque
from pyautogui import press, click, screenshot
from time import sleep
from coordinateManager import CoordinateManager, Point, Box
from PIL import Image, ImageEnhance, ImageGrab, ImageFilter

def pressKey(amount : int, key : str) -> None:
    press(key, presses=amount, interval=0.2)

class Tank:
    def __init__(self, boundaries : Box, color : tuple[int, int, int], coordManager : CoordinateManager) -> None:
        self.__position : Point = Point(0.5, 0.5)
        
        self.__boundaries : Box = boundaries
        self.__color : tuple[int, int, int] = color
        
        self.__lastAngle : int = 0
        self.__lastPower : int = 0
        self.coordManager = coordManager
        
    def getXCoordinate(self) -> float:
        return self.__position.getX()
    
    def getYCoordinate(self) -> float:
        return self.__position.getY()
    
    def getAbsoluteXCoordinate(self) -> int:
        return self.coordManager.convertFloatToWidth(self.getXCoordinate())
    
    def getAbsoluteYCoordinate(self) -> int:
        return self.coordManager.convertFloatToHeigth(self.getYCoordinate())
    
    def moveCannon(self, angle : int, strength : int) -> None:
        key_angle = "left" if angle <= 90 else "right"
        if angle > 90: key_angle="right"
        
        self.updateAndGetExcactPosition()
        self.resetAngle()
        
        angle_delta = abs(angle-90)
        strengh_delta = abs(100-strength)
        
        pressKey(angle_delta, key_angle)
        pressKey(strengh_delta, "down")
        
    def resetAngle(self) -> None:
        myPosX = self.getAbsoluteXCoordinate()
        myPosY = self.getAbsoluteYCoordinate()
        
        click(myPosX, max(myPosY - self.coordManager.convertFloatToWidth(self.coordManager.RESETANGLERADIUS), 0))

        if myPosY <= 300: pressKey(60, "up")
        else: pressKey(20, "up")
        
    def updateAndGetExcactPosition(self) -> tuple[float, float]:
        myPosX = self.getAbsoluteXCoordinate()
        myPosY = self.getAbsoluteYCoordinate()
        
        click(myPosX, min(myPosY + self.coordManager.convertFloatToHeigth( 0.018519), self.coordManager.convertFloatToHeigth(0.814815)))
        sleep(0.05)
        
        screenshotBoundarie = self.coordManager.SHOOTLINE_FIELD.getBoundariesNormalized(self.coordManager)
        
        height = screenshotBoundarie[3]
        if max(myPosY+screenshotBoundarie[1],0) == 0:
            height = abs(screenshotBoundarie[1])-myPosY[1]
        cap = screenshot(region=(myPosX+screenshotBoundarie[0], max(myPosY+screenshotBoundarie[1],0), screenshotBoundarie[2]*2, height))

        enhancer = ImageEnhance.Sharpness(cap)
        cap = enhancer.enhance(1000)
        enhancer = ImageEnhance.Contrast(cap)
        cap = enhancer.enhance(10)

        firstaxs = []
        for x in range(0,cap.width):
            for y in range(0,cap.height):
                color = cap.getpixel((x, y))
                if color == (255,255,255): firstaxs.append(x)
                else: cap.putpixel((x,y),(0,0,0))

        allxs = []
        for x in firstaxs:
            if x not in allxs: allxs.append(x)

        cap = cap.crop((0,2,cap.width,cap.height-2))
        highest_row = 0
        highest_count = 0
        for x in allxs:
            count = 0
            for y in range(cap.height):
                color = cap.getpixel((x, y))
                if color == (255,255,255): count += 1
            if count == cap.height:
                for y in range(cap.height):
                    color = cap.getpixel((x+1, y))
                    if color == (255,255,255): count += 1
            if count > highest_count:
                highest_row = x
                highest_count = count

        myPosX = myPosX + screenshotBoundarie[0] + highest_row
        myPosX = self.coordManager.convertWidthToFloat(myPosX)
        
        self.__position.setX(myPosX)
        return myPosX, myPosY
    
    def getAverageCoordinatesBreadth(self, everyPixel=2) -> tuple[float, float]:
        myPosX = self.getAbsoluteXCoordinate()
        myPosY = self.getAbsoluteYCoordinate()
        
        gamefieldBoundaries = self.coordManager.GAME_FIELD.getBoundariesNormalized(self.coordManager)
        
        s = ImageGrab.grab(bbox = (gamefieldBoundaries[0],gamefieldBoundaries[1],gamefieldBoundaries[2],gamefieldBoundaries[3]))
        q = deque()
        visited = set()
        
        everyPixelTimes2, everyPixelTimes3 = everyPixel * 2, everyPixel * 3

        q.append(myPosX)
        q.append(myPosY)
        
        visited.add((myPosX, myPosY))
        minD = [0,0,float("inf")]

        while q:
            field = (q.popleft(), q.popleft())
            
            if not (field[0] < gamefieldBoundaries[2] and field[0] >= gamefieldBoundaries[0] and field[1] < gamefieldBoundaries[3] and field[1] >= gamefieldBoundaries[1]):
                continue
            
            color = s.getpixel((field[0], field[1]))
            d = numpy.linalg.norm(numpy.array(color) - numpy.array(self.__color))
            
            if d < minD[2]: minD = [field[0], field[1], d]
            if d < 15: break

            if (field[0] + everyPixel, field[1]) not in visited:
                q.append(field[0] + everyPixel)
                q.append(field[1])

                visited.add((field[0] + everyPixel, field[1]))
                
            if (field[0] - everyPixel, field[1]) not in visited:
                q.append(field[0] - everyPixel)
                q.append(field[1])

                visited.add((field[0] - everyPixel, field[1]))
            if (field[0], field[1] + everyPixel) not in visited:
                q.append(field[0])
                q.append(field[1] + everyPixel)

                visited.add((field[0], field[1] + everyPixel))
                
            if (field[0], field[1] - everyPixel) not in visited:
                q.append(field[0])
                q.append(field[1] - everyPixel)
                visited.add((field[0], field[1] - everyPixel))

        myPosX = self.coordManager.convertWidthToFloat(minD[0])
        myPosY = self.coordManager.convertHeigthToFloat(minD[1])
        self.__position.setX(myPosX)
        self.__position.setY(myPosY)
        
        return (myPosX, myPosY)
    
if __name__ == "__main__":
    sleep(2)
    CM = CoordinateManager()
    myTank = Tank(CM.TANK1BOX, (36, 245, 41), CM)
    
    print(myTank.getAverageCoordinatesBreadth(everyPixel=3))
    visualizer.drawSquareAroundPixel(myTank.getAbsoluteXCoordinate(), myTank.getAbsoluteYCoordinate(), 15, CM, "Z_bild.png")
    myTank.moveCannon(80,90)