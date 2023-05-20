import kNearestNeighbors as knn
import pyautogui

from coordinateManager import CoordinateManager, Box
from PIL import Image, ImageEnhance, ImageGrab
from definitions import WEPS

class GameEnvironment:
    def __init__(self, coordManager : CoordinateManager) -> None:
        """a class for managing the Environment like pressing buttons or read out text

        Args:
            coordManager (CoordinateManager): an initlaized CoordinateManager class
        """        
        self.coordManager = coordManager
        
        self.__WEAPONPIXELS = self.__loadPixelData('data/WeaponPixels.txt') 
        self.__WINDPIXELS = self.__loadPixelData('data/WindPixels.txt')
        
        self.FireButton : str = ("Images/FireButton.png", coordManager.FIRE_BUTTON)
        self.LockedInButton : str = ("Images/LockedInButton.png", coordManager.FIRE_BUTTON)
        self.NotFireButton : str = ("Images/NotFireButton.png", coordManager.FIRE_BUTTON)
        self.ReadyButton : str = ("Images/ReadyButton.png", coordManager.READY_BUTTON)
        
        self.isShootingState = False
        self.inLobbyState = False
        
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
            if count % 30 == 0: print(f"{count} von {len(Lines)} geladen")
        print(f"{count} von {len(Lines)} geladen")
        
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
    
    def getWindRichtung(self) -> int:
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
        cap = self.__makeScreenFromWind()
        arr, ones = self.__convertTo1DArray(cap)
        new_point = arr
        wind = knn.multiThreadfindCategory(new_point, self.__WINDPIXELS, 8, ones, fixedK=1)
        return int(wind), self.getWindRichtung()

    def pressButton(self, button : tuple[str, Box]) -> None:
        button = pyautogui.locateOnScreen(button[0], grayscale=True, confidence=0.9, region=button[1].getBoundariesNormalized(self.coordManager))
        if button == None: return
        pyautogui.click(button[0],button[1])
        pyautogui.click(5,5)
    
    def inLobby(self):
        inLobby = pyautogui.locateOnScreen(self.ReadyButton[0], grayscale=True, confidence=0.9, region=self.ReadyButton[1].getBoundariesNormalized(self.coordManager))
        if inLobby:
            self.inLobbyState = True
            return True
        else: 
            self.inLobbyState = False
            return False
        
    def inLoadingScreen(self):
        FireButton = pyautogui.locateOnScreen(self.FireButton[0], confidence=0.9, region=self.FireButton[1].getBoundariesNormalized(self.coordManager))
        NotFireButton = pyautogui.locateOnScreen(self.NotFireButton[0], confidence=0.9, region=self.NotFireButton[1].getBoundariesNormalized(self.coordManager))
        ReadyButton = pyautogui.locateOnScreen(self.ReadyButton[0], confidence=0.9, region=self.ReadyButton[1].getBoundariesNormalized(self.coordManager))
        LockedInButton = pyautogui.locateOnScreen(self.LockedInButton[0], confidence=0.9, region=self.LockedInButton[1].getBoundariesNormalized(self.coordManager))
        
        if not FireButton and not NotFireButton and not ReadyButton and not LockedInButton:
            return True
        return False
    
    def isMyTurn(self):
        myTurn = pyautogui.locateOnScreen(self.FireButton[0], confidence=0.9, region=self.FireButton[1].getBoundariesNormalized(self.coordManager))
        if myTurn == None:
            return False
        else: return True
    
if __name__ == "__main__":
    CoordMan = CoordinateManager()
    GameEnv = GameEnvironment(CoordMan)
    while True:
        print("lobby", GameEnv.inLobby(), "loading", GameEnv.inLoadingScreen())