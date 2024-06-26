import numpy
import shootingStrategies
import colors
import visualizer
import colorama
import globals
import random

from math import sqrt
from scipy.spatial import distance
from colorama import Fore, Back, Style
from collections import deque
from pyautogui import press, click, screenshot, keyDown, keyUp
from time import sleep
from coordinateManager import CoordinateManager, Point, Box
from environment import GameEnvironment
from PIL import ImageEnhance, ImageGrab, ImageDraw
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

class TankCollection:
    def __init__(self, color : tuple[int, int, int], coordManager : CoordinateManager, minimum = 1, maximum = 7,hideTanks=None, name="Enemy"):
        """A wrapper for holding all enemy tanks. Inplies that there is atleast one enemy

        Args:
            color (tuple[int, int, int]): color of the enemy tanks. one that is the most common in him
            coordManager (CoordinateManager): coordinate Manager class
            ownTank: An own tank to make it hide
        """
        self.color = color
        self.coordManager = coordManager
        self.tanks = []
        self.minimum = minimum
        self.maximum = maximum
        self.name = name
        
        self.initTankCollection(hideTanks=hideTanks)
        
    def initTankCollection(self, hideTanks=None):
        hideRegions = self.coordManager.convertTanksToHideRegion(hideTanks) + self.coordManager.convertTanksToHideRegion(self.tanks)
        
        while True:
            newEnemy = Tank(self.color, self.coordManager, name=f"{self.name} Tank {len(self.tanks) + 1}")
            res = newEnemy.getCoordinatesBrute(hideRegions=hideRegions)
            
            if res[1] >= 15:
                print(f"Found {len(self.tanks)} Tanks in collection!")
                
                #try again if no one is found
                if len(self.tanks) < self.minimum:
                    self.initTankCollection()
                    
                return
            
            hr = self.coordManager.convertTanksToHideRegion([newEnemy])
            hideRegions.extend(hr)
            self.tanks.append(newEnemy)
            
            if len(self.tanks) >= self.maximum:
                print(f"Found {len(self.tanks)} Tanks in collection!")
                return
        
    def updateTankCollection(self, hideTanks=None):
        hideRegions = self.coordManager.convertTanksToHideRegion(hideTanks)
        for tank in self.tanks:
            if not tank.isInSameSpot():
                tank.getCoordinatesBreadth(hideRegions = hideRegions)
                
        #Sort out Tanks that have the same coordinate
        newTanks = []
        for tank in self.tanks:
            add = True
            for otherTank in newTanks:
                if tank.areCloseToEachOther(otherTank):
                    add = False
            #Check if Enemy is in the CANTBEANYONE Region. This is normally where allies are located but there are none.
            if self.coordManager.CANTBEANYONE.isPointInBoundaries(tank.getPosition()): add = False
            if add: newTanks.append(tank)
            else: print(f"deleted {tank}")
                
        self.tanks = newTanks    
    
    def paintTanks(self):
        for enemyTank in self.tanks:
            enemyTank.paintTank()

class Tank:
    def __init__(self, color : tuple[int, int, int], coordManager : CoordinateManager, name : str ="Tank", epsilon : float = 0.006):
        """Tank class to store variables as position and color
        to quickly find them and also convert coordinates to absolute units
        and relative units.

        Args:
            color (tuple[int, int, int]): color of the tank. one that is the most common in him
            coordManager (CoordinateManager): coordinate Manager class
            name (str, optional): name of the tank for better identification. Defaults to "Tank".
            epsilon (float, optional): Radius of the tank. Defaults to 0.006.
        """
        
        self.__position : Point = Point(0.5, 0.5)
        self.color = color
        self.coordManager = coordManager
        self.name = name
        self.epsilon = epsilon
    
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
    
    @timeit("getCoordinatesBreadth")
    def getCoordinatesBreadth(self, everyPixel=3, hideRegions=None) -> tuple[Point, float]:
        """updates the coordinates of the tank by doing breathsearch on the screen from the last position
        updates them automatically but also returns them. Position may be inaccurate by a few pixels.

        Args:
            everyPixel (int, optional): skips all the pixels in between for much better performance. Defaults to 3.
            hideRegions (list[Box], optional): a list of boxes, that is going to be hidden

        Returns:
            Point: Point class of the current position
            float: the closest distance of the color to another color
        """
        myPosX = self.absX
        myPosY = self.absY
        
        gamefieldBoundaries = self.coordManager.GAME_FIELD.getBoundariesNormalized(self.coordManager)
        
        s = ImageGrab.grab(bbox = (gamefieldBoundaries[0],gamefieldBoundaries[1],gamefieldBoundaries[2],gamefieldBoundaries[3]))
        
        #regions to cover
        if hideRegions == None:
            hideRegions = []
            
        draw = ImageDraw.Draw(s)
        for region in hideRegions:
            regionBoundaries = region.getBoundariesNormalized(self.coordManager)
            draw.rectangle([regionBoundaries[0], regionBoundaries[1], regionBoundaries[2], regionBoundaries[3]], fill=(0, 0, 0))
        del draw

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
    
    @timeit("getCoordinatesBrute")
    def getCoordinatesBrute(self, everyPixel=1, hideRegions=None) -> tuple[Point, float]:
        """updates the coordinates of the tank by doing brute force search on the screen
        updates them automatically but also returns them. Position may be inaccurate by a few pixels.

        Args:
            everyPixel (int, optional): skips all the pixels in between for much better performance. Defaults to 3.
            hideRegions (list[Box], optional): a list of boxes, that is going to be hidden

        Returns:
            Point: Point class of the current position
            float: the closest distance of the color to another color
        """
        gamefieldBoundaries = self.coordManager.GAME_FIELD.getBoundariesNormalized(self.coordManager)
        image = ImageGrab.grab(bbox = (gamefieldBoundaries[0],gamefieldBoundaries[1],gamefieldBoundaries[2],gamefieldBoundaries[3]))
        
        #regions to cover
        if hideRegions == None:
            hideRegions = []
        
        draw = ImageDraw.Draw(image)
        for region in hideRegions:
            regionBoundaries = region.getBoundariesNormalized(self.coordManager)
            draw.rectangle([regionBoundaries[0], regionBoundaries[1], regionBoundaries[2], regionBoundaries[3]], fill=(0, 0, 0))
        del draw

        image = numpy.array(image)
        #image = image[:, :, ::-1]

        subset_image = image[::everyPixel, ::everyPixel]
        color_distances = distance.cdist([self.color], subset_image.reshape(-1, 3)).squeeze()

        min_distance_idx = numpy.argmin(color_distances)
        min_distance = color_distances[min_distance_idx]

        y, x = numpy.unravel_index(min_distance_idx, subset_image.shape[:2])
        x, y = x * everyPixel, y * everyPixel
        
        self.absX = x
        self.absY = y
        
        return (Point(self.getXCoordinate(), self.getYCoordinate()), min_distance)
    
    @timeit(print_result=True)
    def isInSameSpot(self) -> bool:
        """Checks if a tank is still in the spot as it was before. It can be used to skip searching the screen for it

        Returns:
            bool: True if tank has not moved, False if it has
        """
        delta = self.coordManager.SAMETANKBOX.getBoundariesNormalized(self.coordManager)
        s = ImageGrab.grab(bbox=(self.absX + delta[0], self.absY + delta[1], self.absX + delta[2], self.absY + delta[3]))

        smallestD = float("inf")

        image_array = numpy.array(s)

        color_diff = numpy.linalg.norm(image_array - numpy.array(self.color), axis=2)
        smallestD = numpy.min(color_diff)

        if smallestD <= 15:
            return True
        else:
            return False
    
    def isPointHitting(self, x : float, y : float) -> bool:
        """checks if a given coordinate is in hit range to an tank.
        it compares the relative coordinates of the tank!

        Args:
            x (float): x coordinate.
            y (float): y coordinate.

        Returns:
            bool: returns True if a coordinate is in the given range
        """
        if not (self.getXCoordinate() - self.epsilon       <= x <= self.getXCoordinate() + self.epsilon):       return False
        if not (self.getYCoordinate() - self.epsilon * self.coordManager.getWidthHeightRatio() <= y <= self.getYCoordinate() + self.epsilon * self.coordManager.getWidthHeightRatio()): return False
        return True
    
    def areCloseToEachOther(self, other) -> bool:
        """Checkfs if two tanks are consideres close to each other

        Args:
            other (Tank): the other Tank

        Returns:
            bool: True if close, False otherwise
        """
        if sqrt((self.getXCoordinate() - other.getXCoordinate())**2 + (self.getYCoordinate() - other.getYCoordinate())**2) < 0.03:
            return True
        return False
    
    def paintTank(self) -> None:
        visualizer.paintPixels(self.getPosition(), self.epsilon * self.coordManager.getScreenWidth(), self.color, self.coordManager)
    
    def __repr__(self) -> str:
        text = f"{Style.BRIGHT}{colors.convert_rgb_to_text_color(self.color)}{self.name}{Style.RESET_ALL}: | Positon: {self.__position}"
        return text

class friendlyTank(Tank):
    def __init__(self, color : tuple[int, int, int], coordManager : CoordinateManager, gameEnvironment : GameEnvironment, name : str = "friendlyTank", epsilon : float = 0.006) -> None:
        """Addition to tank class. Can also control a tank. It has the ability to shoot and move your cannon.

        Args:
            color (tuple[int, int, int]): color of the tank. one that is the most common in him
            coordManager (CoordinateManager): initialized CoordinateManager class
            gameEnvironment (GameEnvironment): initialized GameEnvironment class
            name (str, optional): _description_. Defaults to "Tank".
            delta (float, optional): _description_. Defaults to 0.01.
        """
        super().__init__(color, coordManager, name=name, epsilon=epsilon)
        
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
        
    def shoot(self, enemyTanks, onlyOne=False, executeShoot=True) -> None:
        """let the tank shoot, it does not check if it is aviable to shoot
        and just proceeds with his procedure as he is able to shoot
        only call if tank is aviable to shoot

        Args:
            enemyTank (TankCollection): TankCollection class so it can choose its target
            onlyOne (bool, optional): it should only calculate one random target. Defaults to False.
            executeShoot (bool, optional): Clicks on the buttons to execute the shot. Defaults to True.
        """
        
        weapon, weapon_category, weapon_extra_info = self.gameEnvironment.getWeapon()
        wind, wind_richtung = self.gameEnvironment.getWind()
        wind = wind * wind_richtung
        print(f"{super().__repr__()}: | {weapon=} | {weapon_category=} | {weapon_extra_info=} | {wind=}")
        
        buffs = self.gameEnvironment.findBuffs()
        
        #convert buffs to tanks
        key_to_epsilon = {"x3": 0.01, "x2": 0.02, "drone": 0.008, "crate": 0.005}
        for key in buffs:
            newList = []
            for buff in buffs[key]:
                buffTank = Tank(colors.GEAR, self.coordManager, name=key, epsilon=key_to_epsilon[key])
                buffTank.setPosition(buff)
                newList.append(buffTank)
            buffs[key] = newList
            
        print(f"{buffs=}")
        
        groundColor = self.gameEnvironment.getGroundColor()
        
        calculations = shootingStrategies.getAngleAndPower(self, enemyTanks, weapon_category, wind, weapon_extra_info, buffs, self.coordManager, groundColor, onlyOne=onlyOne)
        
        b = [calculations[i] for i in calculations]
        maxElem = max(b, key=lambda x: x[1])[1]
        b = list(filter(lambda x: x[1] == maxElem, sorted(b, key=lambda x: x[1], reverse=True)))
        
        
        c = random.choice(b)
        angle, power = c[0]
        
        if weapon_category != "instant" and executeShoot:
            self.moveCannon(angle, power)
            
        if executeShoot:
            self.gameEnvironment.pressButton(self.gameEnvironment.FireButton)
            click(50, 200)
        
        if globals.CREATE_PICTURE:
            for array in buffs.values():
                for b in array:
                    b.paintTank()
    
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
    
    def setBoundaries(self, enemyTanks, mateTanks) -> None:
        offset = 0.1
        allTanks = [self] + enemyTanks.tanks + mateTanks.tanks
        allTanks = sorted(allTanks, key=lambda x: x.getXCoordinate())
        
        boundingIndex = allTanks.index(self)
        numTanks = len(allTanks)
        start = (1 / numTanks) * boundingIndex + offset / 2
        end = (1 / numTanks) * (boundingIndex + 1) - offset / 2
        
        self.BOUNDARIES = Box(start, 0, end, 1)
    
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
    
    globals.CREATE_PICTURE = True
    #sleep(1)
    visualizer.createImage(CM)
    
    myTank = friendlyTank(colors.TANK_OWN, CM, GE, name="Mein Panzer")
    myTank.getCoordinatesBrute()
    myTank.paintTank()
    
    mateTanks = TankCollection(colors.TANK_MATE, CM, hideTanks=[myTank], minimum=0)
    mateTanks.paintTanks()
    
    ground = GE.getGroundColor()
    enemyColor = colors.convert_ground_to_enemy_color(ground)
    enemyTanks = TankCollection(enemyColor, CM, hideTanks=mateTanks.tanks + [myTank])
    enemyTanks.paintTanks()
    
    myTank.shoot(enemyTanks)
    
    visualizer.saveImage()