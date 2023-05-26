import kNearestNeighbors as knn
import pyautogui
import threading

from coordinateManager import CoordinateManager, Box, Point
from PIL import Image, ImageEnhance, ImageGrab
from definitions import WEPS
from decorators import timeit

class GameEnvironment:
    @timeit("Class: GameEnvironment __init__")
    def __init__(self, coordManager : CoordinateManager) -> None:
        """a class for managing the Environment like pressing buttons or read out text

        Args:
            coordManager (CoordinateManager): an initlaized CoordinateManager class
        """        
        self.coordManager = coordManager
        
        self.__WEAPONPIXELS = self.__loadPixelData('data/WeaponPixels.txt') 
        self.__WINDPIXELS = self.__loadPixelData('data/WindPixels.txt')
        
        #Buttons
        self.FireButton : tuple[str, CoordinateManager] = ("Images/FireButton.png", coordManager.FIRE_BUTTON)
        self.LockedInButton : tuple[str, CoordinateManager] = ("Images/LockedInButton.png", coordManager.FIRE_BUTTON)
        self.NotFireButton : tuple[str, CoordinateManager] = ("Images/NotFireButton.png", coordManager.FIRE_BUTTON)
        self.ReadyButton : tuple[str, CoordinateManager] = ("Images/ReadyButton.png", coordManager.READY_BUTTON)
        
        #Perks
        self.x2 : tuple[str, CoordinateManager] = ("Images/x2.png", coordManager.X2)
        self.x3 : tuple[str, CoordinateManager] = ("Images/x3.png", coordManager.X3)
        
        self.__isShootingState = False
        self.shootingStateEvent = threading.Event()
        self.__inLobbyState = False
        self.lobbyStateEvent = threading.Event()
    
    @property
    def isShootingState(self) -> bool:
        """returns if the envioronment is currently in a state where the tank is shooting

        Returns:
            bool: True if shooting, else False
        """
        return self.__isShootingState
    
    @isShootingState.setter
    def isShootingState(self, value : bool) -> None:
        """Sets the state to the wished value. Also sets the flag accordingly for threads to work with
        Event will be flagged to true when the value is False.
        When you are shooting, the flag will be false so no thread is currently working.

        Args:
            value (bool): True or False if in Shooting State

        Raises:
            TypeError: if not True or False
        """
        self.__isShootingState = value
        if value:
            self.shootingStateEvent.clear()
        elif not value:
            self.shootingStateEvent.set()
        else:
            raise TypeError()

    @property
    def inLobbyState(self) -> bool:
        """returns if the envioronment is currently in a state where they are in the lobby

        Returns:
            bool: True if in lobby, else False
        """
        return self.__inLobbyState 
    
    @inLobbyState.setter
    def inLobbyState(self, value : bool) -> None:
        """Sets the state to the wished value. Also sets the flag accordingly for threads to work with
        Event will be flagged to true when the value is False.
        When you are in the Lobby, the flag will be false so no thread is currently working.

        Args:
            value (bool): True or False if in Lobby

        Raises:
            TypeError: if not True or False
        """
        self.__inLobbyState = value
        if value:
            self.lobbyStateEvent.clear()
        elif not value:
            self.lobbyStateEvent.set()
        else:
            raise TypeError()
    
    def __loadPixelData(self, path : str) -> list[list[int], str, int]:
        """loads data out of a txt file for KNN-Recognition

        Args:
            path (str): path to the txt file

        Returns:
            list[list[int], str, int]: a list of all the data
        """
        file = open(path, 'r')
        Lines = file.readlines()
        data = []
        
        count = 0
        for line in Lines:
            count += 1
            txt = "{}".format(line.strip())
            d = txt.split(" ")
            for i in range(2,len(d)):
                d[i] = int(d[i])
            data.append([d[2:], d[0].replace("#"," "), int(d[1])])        
        return data
    
    def __makeScreenFromWeapons(self) -> Image:
        """makes a screenshot and applies different filters for weapon recognition

        Returns:
            Image: returns the edited image
        """
        screenshotBoundarie = self.coordManager.WEAPON_FIELD.getBoundariesNormalized(self.coordManager)
        cap = ImageGrab.grab(bbox = (screenshotBoundarie[0],screenshotBoundarie[1],screenshotBoundarie[2],screenshotBoundarie[3]))
        filter = ImageEnhance.Color(cap)
        cap = filter.enhance(50)
        enhancer = ImageEnhance.Contrast(cap)
        cap = enhancer.enhance(1)
        
        newCap  = Image.new(mode = "RGB", size = (cap.width, cap.height), color = (0, 0, 0))
        for x in range(cap.width):
            for y in range(cap.height):
                color = cap.getpixel((x, y))
                if color[0] >= 230 and color[1] >= 230 and color[2] >= 230: 
                    newCap.putpixel((x,y),(255,255,255))
                else:
                    newCap.putpixel((x,y),(0,0,0))
        return newCap

    def __makeScreenFromWind(self) -> Image:
        """makes a screenshot and applies different filters for wind recognition

        Returns:
            Image: returns the edited image
        """
        screenshotBoundarie = self.coordManager.WIND_FIELD.getBoundariesNormalized(self.coordManager)
        cap = ImageGrab.grab(bbox = (screenshotBoundarie[0],screenshotBoundarie[1],screenshotBoundarie[2],screenshotBoundarie[3]))

        filter = ImageEnhance.Color(cap)
        new_cap = filter.enhance(0)
        enhancer = ImageEnhance.Contrast(new_cap)
        new_cap = enhancer.enhance(100)

        newCap  = Image.new(mode = "RGB", size = (cap.width, cap.height), color = (0, 0, 0))
        for x in range(cap.width):
            for y in range(cap.height):
                color = cap.getpixel((x, y))
                if color[0] <= 70 and color[1] <= 70 and color[2] <= 70: 
                    newCap.putpixel((x,y),(255,255,255))
                else:
                    newCap.putpixel((x,y),(0,0,0))
        return newCap

    def __convertTo1DArray(self, cap):
        """generates a screenshot to a list of ones and zeros based on gray-scale value

        Args:
            cap (_type_): an image that was edited already

        Returns:
            (list, int): returns the list ones and zeros and number of ones
        """
        arr = []
        num = 0
        for x in range(cap.width):
            for y in range(cap.height):
                color = cap.getpixel((x, y))
                c = round(0.2989 * color[0] + 0.5870 * color[1] + 0.1140 * color[2])
                if c == 255:
                    arr.append(1)
                    num += 1
                else: arr.append(0)
        return (arr, num)
    
    def getSelectedWeapon(self) -> tuple[str, str]:
        """reads out the screen for the current selected weapon

        Returns:
            tuple[str, str, int]: returns (weapon_name, weapon_category, extra_information like delta angle)
        """
        cap = self.__makeScreenFromWeapons()
        arr, ones = self.__convertTo1DArray(cap)
        new_point = arr
        wep_str = knn.multiThreadfindCategory(new_point, self.__WEAPONPIXELS, 8, ones, fixedK=1)
        
        extra_information = None
        for wep_cat in WEPS:
            for wep in WEPS[wep_cat]:
                if type(wep) is tuple:
                    extra_information = wep[1]
                    wep = wep[0]
                if wep == wep_str: return wep, wep_cat, extra_information
        return ("shot", "normal", None)
    
    def __getWindRichtung(self) -> int:
        """reads out the screen for the current wind direction

        Returns:
            int: returns 1 for right, -1 for left, 1 is default to not mess up calculations
        """
        windFieldLeftBoundaries = self.coordManager.WIND_FIELD_LEFT.getBoundariesNormalized(self.coordManager)
        windFieldRightBoundaries = self.coordManager.WIND_FIELD_RIGHT.getBoundariesNormalized(self.coordManager)
        
        richtung = 1
        for CORDS in (windFieldLeftBoundaries, windFieldRightBoundaries):
            cap = ImageGrab.grab(bbox = (CORDS[0],CORDS[1],CORDS[2],CORDS[3]))
            filter = ImageEnhance.Color(cap)
            cap = filter.enhance(0)
            enhancer = ImageEnhance.Contrast(cap)
            cap = enhancer.enhance(100)
            if cap.getpixel((int(cap.width/2),int(cap.height/2))) == (255,255,255):
                if CORDS == windFieldRightBoundaries: richtung = 1
                else: richtung = -1
        return richtung
    
    def getWind(self) -> tuple[int, int]:
        """reads out the screen for the current wind and direction

        Returns:
            tuple[int, int]: returns the wind as an absolute value and the wind direction it goes in. 68 to the left would be (68,-1)
        """
        cap = self.__makeScreenFromWind()
        arr, ones = self.__convertTo1DArray(cap)
        new_point = arr
        wind = knn.multiThreadfindCategory(new_point, self.__WINDPIXELS, 8, ones, fixedK=1)
        return int(wind), self.__getWindRichtung()

    def pressButton(self, button : tuple[str, Box]) -> None:
        """presses a button that. Only presses is button is present on the screen

        Args:
            button (tuple[tuple[str, CoordinateManager], Box]): a button
        """
        button = pyautogui.locateOnScreen(button[0], grayscale=True, confidence=0.9, region=button[1].getBoundariesNormalized(self.coordManager))
        if button == None: return
        pyautogui.click(button[0],button[1])
        pyautogui.click(5,5)
    
    def inLobby(self) -> bool:
        """checks the screen if it is in the currently in the lobby
        will set the inLobby State according to it, but will also return it

        Returns:
            bool: True if in lobby, else False
        """
        inLobby = pyautogui.locateOnScreen(self.ReadyButton[0], grayscale=True, confidence=0.9, region=self.ReadyButton[1].getBoundariesNormalized(self.coordManager))
        if inLobby:
            self.inLobbyState = True
            return True
        else: 
            self.inLobbyState = False
            return False
        
    def inLoadingScreen(self) -> bool:
        """chcecks the screen if it is in the loading Screen

        Returns:
            bool: True if in loading screen. else False
        """
        FireButton = pyautogui.locateOnScreen(self.FireButton[0], confidence=0.9, region=self.FireButton[1].getBoundariesNormalized(self.coordManager))
        NotFireButton = pyautogui.locateOnScreen(self.NotFireButton[0], confidence=0.9, region=self.NotFireButton[1].getBoundariesNormalized(self.coordManager))
        ReadyButton = pyautogui.locateOnScreen(self.ReadyButton[0], confidence=0.9, region=self.ReadyButton[1].getBoundariesNormalized(self.coordManager))
        LockedInButton = pyautogui.locateOnScreen(self.LockedInButton[0], confidence=0.9, region=self.LockedInButton[1].getBoundariesNormalized(self.coordManager))
        
        if not FireButton and not NotFireButton and not ReadyButton and not LockedInButton:
            return True
        return False
    
    def isMyTurn(self) -> bool:
        """chcecks the screen if it is my turn to play

        Returns:
            bool: True if it my turn, else False
        """
        myTurn = pyautogui.locateOnScreen(self.FireButton[0], confidence=0.9, region=self.FireButton[1].getBoundariesNormalized(self.coordManager))
        if myTurn == None:
            return False
        else: return True
    
    def findPicture(self, button : tuple[str, Box]) -> Point:
        """_summary_

        Args:
            button (tuple[str, Box]): a button

        Returns:
            Point: a point where the picture is located, None if not found
        """
        location = pyautogui.locateOnScreen(button[0], grayscale=True, confidence=0.9, region=button[1].getBoundariesNormalized(self.coordManager))
        if location == None:
            return None
        return Point(self.coordManager.convertWidthToFloat(location[0]), self.coordManager.convertHeigthToFloat(location[1]))
        
if __name__ == "__main__":
    CoordMan = CoordinateManager()
    GameEnv = GameEnvironment(CoordMan)
    while True:
        print(GameEnv.findPicture(GameEnv.circleBumper))