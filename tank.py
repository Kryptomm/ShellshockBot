import numpy
import visualizer
import shootingStrategies
from collections import deque
from pyautogui import press, click, screenshot, locateOnScreen, keyDown, keyUp
from time import sleep
from coordinateManager import CoordinateManager, Point, Box
from environment import GameEnvironment
from PIL import Image, ImageEnhance, ImageGrab, ImageFilter

def pressKey(amount : int, key : str) -> None:
    press(key, presses=amount, interval=0.05)

def holdKey(time : float, key : str):
    keyDown(key)
    sleep(time)
    keyUp(key)

class Tank:
    def __init__(self, color : tuple[int, int, int], coordManager : CoordinateManager):
        self.__position : Point = Point(0.5, 0.5)
        self.color = color
        self.coordManager = coordManager
        
    def getPosition(self) -> Point:
        return self.__position
    
    def getXCoordinate(self) -> float:
        return self.__position.getX()
    
    def getYCoordinate(self) -> float:
        return self.__position.getY()
    
    @property
    def absX(self) -> int:
        return self.coordManager.convertFloatToWidth(self.getXCoordinate())
    
    @absX.setter
    def absX(self, value : int) -> None:
        self.__position.setX(self.coordManager.convertWidthToFloat(value))
    
    @property
    def absY(self) -> int:
        return self.coordManager.convertFloatToHeigth(self.getYCoordinate())
    
    @absY.setter
    def absY(self, value : int) -> None:
        self.__position.setY(self.coordManager.convertHeigthToFloat(value))

    def getAverageCoordinatesBreadth(self, everyPixel=3) -> Point:
        myPosX = self.absX
        myPosY = self.absY
        
        gamefieldBoundaries = self.coordManager.GAME_FIELD.getBoundariesNormalized(self.coordManager)
        
        s = ImageGrab.grab(bbox = (gamefieldBoundaries[0],gamefieldBoundaries[1],gamefieldBoundaries[2],gamefieldBoundaries[3]))
        q = deque()
        visited = set()
        
        q.append(myPosX)
        q.append(myPosY)
        
        visited.add((myPosX, myPosY))
        minD = [0,0,float("inf")]

        while q:
            field = (q.popleft(), q.popleft())
            
            if not (field[0] < gamefieldBoundaries[2] and field[0] >= gamefieldBoundaries[0] and field[1] < gamefieldBoundaries[3] and field[1] >= gamefieldBoundaries[1]):
                continue
            
            color = s.getpixel((field[0], field[1]))
            d = numpy.linalg.norm(numpy.array(color) - numpy.array(self.color))
            
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

        self.absX = minD[0]
        self.absY = minD[1]

        return Point(self.getXCoordinate(), self.getYCoordinate())
    

class friendlyTank(Tank):
    def __init__(self, color : tuple[int, int, int], coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
        super().__init__(color, coordManager)
        
        self.BOUNDARIES : Box = None
        self.__lastAngle : int = 0
        self.__lastStrength : int = 0
        self.__firstShot = True
        
        self.gameEnvironment = gameEnvironment
        
        self.shooting = False
        self.SHOOTRADIUS = 0.173958
    
    def moveCannon(self, angle : int, strength : int) -> None:
        angle = angle % 360
        lastAngle = self.__lastAngle
        lastStrength = self.__lastStrength
        
        resetKeyAngle = "right" if angle <= 90 or angle >= 270 else "left"

        resetAngle = abs(angle - 90)
        if resetKeyAngle == "right:":
            resetAngle = 360 - resetAngle
        resetStrength = abs(100-strength)
        
        __toLeft = (lastAngle - angle) % 360
        __toRight = (angle - lastAngle) % 360
        keepAngle = min(__toLeft, __toRight)
        keepKeyAngle = "right" if __toLeft < __toRight else "left"
        
        keepStrength = abs(lastStrength - strength)
        keepKeyStrength = "up" if lastStrength < strength else "down"
        
        isResetting = False
        if (resetAngle + resetStrength < keepAngle + keepStrength) or self.__firstShot:
            isResetting = True
        
        if isResetting:
            self.updateAndGetExcactPosition()
            self.resetAngle()
            pressKey(resetAngle, resetKeyAngle)
            pressKey(resetStrength, "down")
        else:
            pressKey(keepAngle, keepKeyAngle)
            pressKey(keepStrength, keepKeyStrength)
        
        self.__firstShot = False
        self.__lastAngle = angle
        self.__lastStrength = strength
        
    def resetAngle(self) -> None:
        myPosX = self.absX
        myPosY = self.absY
        
        click(myPosX, max(myPosY - self.coordManager.convertFloatToWidth(self.coordManager.RESETANGLERADIUS), 0))

        if myPosY <= 300: pressKey(60, "up")
        else: pressKey(15, "up")
        
    def shoot(self, enemyTank) -> None:
        weapon, weapon_category, extra_info = self.gameEnvironment.getSelectedWeapon()
        wind, wind_richtung = self.gameEnvironment.getWind()
        wind = wind * wind_richtung
        
        angle, power = shootingStrategies.getAngleAndPower(self, enemyTank, weapon_category, wind, extra_info ,self.coordManager)
        
        self.moveCannon(angle, power)
        self.gameEnvironment.pressButton(self.gameEnvironment.FireButton)
    
    def updateAndGetExcactPosition(self) -> Point:
        myPosX = self.absX
        myPosY = self.absY
        
        click(myPosX, min(myPosY + self.coordManager.convertFloatToHeigth( 0.018519), self.coordManager.convertFloatToHeigth(0.814815)))
        sleep(0.05)
        
        screenshotBoundarie = self.coordManager.SHOOTLINE_FIELD.getBoundariesNormalized(self.coordManager)
        
        height = screenshotBoundarie[3]
        if max(myPosY+screenshotBoundarie[1],0) == 0:
            height = abs(screenshotBoundarie[1])-myPosY
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
        self.absX = myPosX
        
        return Point(self.getXCoordinate(), self.getYCoordinate())
    
    def move(self) -> None:
        if self.BOUNDARIES.isPointInBoundaries(self.getPosition()): return False
        
        if self.getXCoordinate() < self.BOUNDARIES.getUpperLeft().getX():
            holdKey(1.25, "d")
        else: holdKey(1.25, "a")
        return True
    
if __name__ == "__main__":
    sleep(2)
    CM = CoordinateManager()
    GE = GameEnvironment(CM)
    
    myTank = friendlyTank((36, 245, 41), CM, GE)
    enemyTank = Tank((194,3,3), CM)
    

    print(myTank.getAverageCoordinatesBreadth(everyPixel=3))
    print(myTank.updateAndGetExcactPosition())
    print(enemyTank.getAverageCoordinatesBreadth(everyPixel=3))
    
    myTank.shoot(enemyTank)