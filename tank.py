import queue
import math
import numpy
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
    
    def pressKey(iterations : int, key : str):
        press(key, presses=iterations, interval=0.2)

    def moveCannon(self, angle : int, strength : int) -> None:
        key_angle = "left" if angle <= 90 else "right"
        if angle > 90: key_angle="right"
        
    def resetAngle(self) -> None:
        myPosX = self.coordManager.convertFloatToWidth(self.getXCoordinate())
        myPosY = self.coordManager.convertFloatToHeigth(self.getYCoordinate())
        
        click(myPosX, max(myPosY - self.coordManager.convertFloatToWidth(self.coordManager.RESETANGLERADIUS), 0))

        if myPosY <= 300: pressKey(60, "up")
        else: pressKey(20, "up")
        
    def updateAndGetExcactPosition(self) -> tuple[float, float]:
        myPosX = self.coordManager.convertFloatToWidth(self.getXCoordinate())
        myPosY = self.coordManager.convertFloatToHeigth(self.getYCoordinate())
        
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
    
    def getAverageCoordinatesBreadth(self, everyPixel=2) -> None:
        myPosX = self.coordManager.convertFloatToWidth(self.getXCoordinate())
        myPosY = self.coordManager.convertFloatToHeigth(self.getYCoordinate())
        
        gamefieldBoundaries = self.coordManager.GAME_FIELD.getBoundariesNormalized(self.coordManager)
        
        s = ImageGrab.grab(bbox = (gamefieldBoundaries[0],gamefieldBoundaries[1],gamefieldBoundaries[2],gamefieldBoundaries[3]))
        q = queue.Queue()
        visited = numpy.zeros((gamefieldBoundaries[2],gamefieldBoundaries[3]), dtype=bool)

        q.put([myPosX, myPosY])
        visited[myPosX][myPosY] = True
        minD = [0,0,float("inf")]

        while not q.empty():
            field = q.get()
            color = s.getpixel((field[0], field[1]))
            d = math.sqrt((color[0]-self.__color[0])**2+(color[1]-self.__color[1])**2+(color[2]-self.__color[2])**2)
            if d < minD[2]: minD = [field[0], field[1], d]

            if d < 15: return minD

            if field[0] + everyPixel < gamefieldBoundaries[2] and not visited[field[0] + everyPixel][field[1]]:
                q.put([field[0] + everyPixel, field[1]])
                visited[field[0] + everyPixel][field[1]] = True
            if field[0] - everyPixel > gamefieldBoundaries[0] and not visited[field[0] - everyPixel][field[1]]:
                q.put([field[0] - everyPixel, field[1]])
                visited[field[0] - everyPixel][field[1]] = True
            if field[1] + everyPixel < gamefieldBoundaries[3] and not visited[field[0]][field[1] + everyPixel]:
                q.put([field[0], field[1] + everyPixel])
                visited[field[0]][field[1] + everyPixel] = True
            if field[1] - everyPixel > gamefieldBoundaries[1] and not visited[field[0]][field[1] - everyPixel]:
                q.put([field[0], field[1] - everyPixel])
                visited[field[0]][field[1] - everyPixel] = True

        myPosX = self.coordManager.convertWidthToFloat(minD[0])
        myPosY = self.coordManager.convertHeigthToFloat(minD[1])
        self.__position.setX(myPosX)
        self.__position.setY(myPosY)
        
        return myPosX, myPosY, minD[2]
    
if __name__ == "__main__":
    sleep(3)
    CM = CoordinateManager()
    myTank = Tank(CM.TANK1BOX, (0, 220, 15), CM)
    
    myTank.getAverageCoordinatesBreadth(everyPixel=2)
    myTank.updateAndGetExcactPosition()
    myTank.resetAngle()