import numpy
import shootingStrategies
import colors
import visualizer
from collections import deque
from pyautogui import press, click, screenshot, keyDown, keyUp
from time import sleep
from coordinateManager import CoordinateManager, Point, Box
from environment import GameEnvironment
from PIL import ImageEnhance, ImageGrab
from decorators import timeit

def pressKey(amount : int, key : str) -> None:
    """Presses a given key on the keyboard x times.

    Args:
        amount (int): amount the key is pressed
        key (str): key to press
    """    
    press(key, presses=amount, interval=0.05)

def holdKey(time : float, key : str) -> None:
    """Holds a key on the keyboard for a given time

    Args:
        time (float): how long the key is pressed in seconds
        key (str): key to hold down
    """    
    keyDown(key)
    sleep(time)
    keyUp(key)

class Tank:
    def __init__(self, color : tuple[int, int, int], coordManager : CoordinateManager, name : str ="Tank"):
        """Tank class to store variables as position and color
        to quickly find them and also convert coordinates to absolute units
        and relative units.

        Args:
            color (tuple[int, int, int]): color of the tank. one that is the most common in him
            coordManager (CoordinateManager): coordinate Manager class
        """
        self.__position : Point = Point(0.5, 0.5)
        self.color = color
        self.coordManager = coordManager
        self.__name = name
    
    def setPosition(self, position : Point) -> None:
        """Sets the position to a new point

        Args:
            position (Point): a Point where the tank is now
        """
        self.__position = position
    
    def getPosition(self) -> Point:
        """getter Function for the Position

        Returns:
            Point: point Class with tanks coordinates
        """        
        return self.__position
    
    def getXCoordinate(self) -> float:
        """getter Function for the relative x coordinate

        Returns:
            float: relative x coordinate [0,1]
        """        
        return self.__position.getX()
    
    def getYCoordinate(self) -> float:
        """getter Function for the relative y coordinate

        Returns:
            float: relative y coordinate [0,1]
        """   
        return self.__position.getY()
    
    @property
    def absX(self) -> int:
        """returns absolute coordiantes of x based on stores relative x and screensize

        Returns:
            int: absolute x coordinate on the screen
        """
        return self.coordManager.convertFloatToWidth(self.getXCoordinate())
    
    @absX.setter
    def absX(self, value : int) -> None:
        """sets the relative x coordinate based on the absolute x position

        Args:
            value (int): absolute x position
        """
        self.__position.setX(self.coordManager.convertWidthToFloat(value))
    
    @property
    def absY(self) -> int:
        """returns absolute coordiantes of y based on stores relative y and screensize

        Returns:
            int: absolute y coordinate on the screen
        """
        return self.coordManager.convertFloatToHeigth(self.getYCoordinate())
    
    @absY.setter
    def absY(self, value : int) -> None:
        """sets the relative y coordinate based on the absolute y position

        Args:
            value (int): absolute y position
        """
        self.__position.setY(self.coordManager.convertHeigthToFloat(value))
    
    @timeit("getAverageCoordinatesBreadth")
    def getAverageCoordinatesBreadth(self, everyPixel=3, hideRegions=None) -> tuple[Point, int]:
        """updates the coordinates of the tank by doing breathsearch on the screen from the last position
        updates them automatically but also returns them. Position may be inaccurate by a few pixels.

        Args:
            everyPixel (int, optional): skips all the pixels in between for much better performance. Defaults to 3.
            hideRegions (list[Box], optional): a list of boxes, that is going to be hidden

        Returns:
            Point: Point class of the current position
            int: the closest distance of the color to another color
        """
        myPosX = self.absX
        myPosY = self.absY
        
        gamefieldBoundaries = self.coordManager.GAME_FIELD.getBoundariesNormalized(self.coordManager)
        
        s = ImageGrab.grab(bbox = (gamefieldBoundaries[0],gamefieldBoundaries[1],gamefieldBoundaries[2],gamefieldBoundaries[3]))
        
        #regions to cover
        if hideRegions == None:
            hideRegions = []
            
        for region in hideRegions:
            regionBoundarie = region.getBoundariesNormalized(self.coordManager)
            for x in range(regionBoundarie[0],regionBoundarie[2]):
                for y in range(regionBoundarie[1],regionBoundarie[3]):
                    try: s.putpixel((x,y),(0,0,0))
                    except: pass

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

        return (Point(self.getXCoordinate(), self.getYCoordinate()), minD[2])
    
    @timeit(print_result=True)
    def isInSameSpot(self) -> bool:
        """Checks if a tank is still in the spot as it was before. It can be used to skip searching the screen for it

        Returns:
            bool: True if tank has not moved, False if it has
        """
        delta = self.coordManager.SAMETANKBOX.getBoundariesNormalized(self.coordManager)
        s = ImageGrab.grab(bbox = (self.absX + delta[0], self.absY + delta[1], self.absX + delta[2], self.absY + delta[3]))

        smallestD = float("inf")
        for x in range(0, s.width, 1):
            for y in range(0, s.height, 1):
                color = s.getpixel((x, y))
                smallestD = min(numpy.linalg.norm(numpy.array(color) - numpy.array(self.color)), smallestD)

        if smallestD <= 15: return True
        return False
    
    def __repr__(self) -> str:
        return f"{self.__name}: | Positon: {self.__position}"

class friendlyTank(Tank):
    def __init__(self, color : tuple[int, int, int], coordManager : CoordinateManager, gameEnvironment : GameEnvironment, name : str = "friendlyTank") -> None:
        """Addition to tank class. Can also control a tank. It has the ability to shoot and move your cannon.

        Args:
            color (tuple[int, int, int]): color of the tank. one that is the most common in him
            coordManager (CoordinateManager): initialized CoordinateManager class
            gameEnvironment (GameEnvironment): initialized GameEnvironment class
        """
        super().__init__(color, coordManager, name=name)
        
        self.BOUNDARIES : Box = None
        self.__lastAngle : int = 0
        self.__lastStrength : int = 0
        self.__firstShot = True
        
        self.gameEnvironment = gameEnvironment
        
        self.shooting = False
        self.SHOOTRADIUS = 0.173958
    
    def moveCannon(self, angle : int, strength : int) -> None:
        """sets your cannon to the given angle and strength.

        Args:
            angle (int): the angle 0 is the direction right and it goes up after [0,359]
            strength (int): strength is as expected [0,100]
        """
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
        """resets the angle to 90,100
        """
        myPosX = self.absX
        myPosY = self.absY
        
        click(myPosX, max(myPosY - self.coordManager.convertFloatToWidth(self.coordManager.RESETANGLERADIUS), 0))

        if myPosY <= 300: pressKey(60, "up")
        else: pressKey(15, "up")
        
    def shoot(self, enemyTank) -> None:
        """let the tank shoot, it does not check if it is aviable to shoot
        and just proceeds with his procedure as he is able to shoot
        only call if tank is aviable to shoot

        Args:
            enemyTank (_type_): a tank class to attack
        """
        weapon, weapon_category, weapon_extra_info = self.gameEnvironment.getSelectedWeapon()
        wind, wind_richtung = self.gameEnvironment.getWind()
        wind = wind * wind_richtung
        
        
        buffPosition = self.gameEnvironment.findPicture(self.gameEnvironment.x3)
        if buffPosition == None:
            buffPosition = self.gameEnvironment.findPicture(self.gameEnvironment.x2)
            
        buffTank = None
        if buffPosition:
            buffTank = Tank((0,0,0), self.coordManager)
            buffTank.setPosition(buffPosition)
            print(f"Buff found at {buffTank.getPosition()}")
            visualizer.paintPixels(buffTank.getPosition()(), 40, (255,144,0), self.coordManager)
        
        angle, power = shootingStrategies.getAngleAndPower(self, enemyTank, weapon_category, wind, weapon_extra_info, buffTank, self.coordManager)
        
        if weapon_category != "instant":
            self.moveCannon(angle, power)
            
        self.gameEnvironment.pressButton(self.gameEnvironment.FireButton)
    
    def updateAndGetExcactPosition(self) -> Point:
        """Will get the excact pixel the tank is located on
        Side effect: will set the cannon something random and it should only be used
        together with resetAngle after
        It will also set the tanks x position to it and will not only return it.
        it updates them automatically.
        Returns:
            Point: the Point where the tank is right now.
        """
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
    
    def move(self) -> bool:
        """moves the tank in direction of the given boundaries if it is not already in there

        Returns:
            bool: has the bot moved or not
        """
        if self.BOUNDARIES.isPointInBoundaries(self.getPosition()): return False
        
        if self.getXCoordinate() < self.BOUNDARIES.getUpperLeft().getX():
            holdKey(1.25, "d")
        else: holdKey(1.25, "a")
        return True
    
    def __repr__(self) -> str:
        baseRepr = super().__repr__()
        return f"{baseRepr} | Angle,Power: {(self.__lastAngle, self.__lastStrength)} "

if __name__ == "__main__":
    CM = CoordinateManager()
    GE = GameEnvironment(CM)
    
    sleep(1)
    myTank = friendlyTank(colors.FRIENDLY_TANK, CM, GE)
    enemyTank = Tank(colors.ENEMY_TANK, CM)
    
