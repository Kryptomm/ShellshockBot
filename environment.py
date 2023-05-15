import kNearestNeighbors as knn

from coordinateManager import CoordinateManager
from PIL import Image, ImageEnhance, ImageGrab
from definitions import WEPS

class GameEnvironment:
    def __init__(self, coordManager : CoordinateManager) -> None:
        self.coordManager = coordManager
        
        self.__inLobby = False
        self.__myTurn = False
        
        self.__WEAPONPIXELS = self.__loadPixelData('data/WeaponPixels.txt') 
        self.__WINDPIXELS = self.__loadPixelData('data/WindPixels.txt')
        
        self.__FireButton = "Images/FireButton.png"
        self.__LockedInButton = "Images/LockedInButton.png"
        self.__NotFireButton = "Images/NotFireButton.png"
        self.__ReadyButton = "Images/ReadyButton.png"
        
    def __loadPixelData(self, path : str) -> None:
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
            if count % 20 == 0: print(f"{count} von {len(Lines)} geladen")
        print(f"{count} von {len(Lines)} geladen")
        
        return data
    
    def __makeScreenFromWeapons(self) -> Image:
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
        return arr, num
    
    def getSelectedWeapon(self) -> tuple[str, str]:
        cap = self.__makeScreenFromWeapons()
        arr, ones = self.__convertTo1DArray(cap)
        new_point = arr
        wep_str = knn.multiThreadfindCategory(new_point, self.__WEAPONPIXELS, 8, ones, fixedK=1)
        
        for wep_cat in WEPS:
            for wep in WEPS[wep_cat]:
                if type(wep) is tuple: wep = wep[0]
                if wep == wep_str: return wep, wep_cat
        return ("shot", "normal")
    
    def getWindRichtung(self) -> str:
        windFieldLeftBoundaries = self.coordManager.WIND_FIELD_LEFT.getBoundariesNormalized(self.coordManager)
        windFieldRightBoundaries = self.coordManager.WIND_FIELD_RIGHT.getBoundariesNormalized(self.coordManager)
        
        richtung = "Rechts"
        for CORDS in (windFieldLeftBoundaries, windFieldRightBoundaries):
            cap = ImageGrab.grab(bbox = (CORDS[0],CORDS[1],CORDS[2],CORDS[3]))
            filter = ImageEnhance.Color(cap)
            cap = filter.enhance(0)
            enhancer = ImageEnhance.Contrast(cap)
            cap = enhancer.enhance(100)
            if cap.getpixel((int(cap.width/2),int(cap.height/2))) == (255,255,255):
                if CORDS == windFieldRightBoundaries: richtung = "Rechts"
                else: richtung = "Links"
        return richtung
    
    def getWind(self) -> tuple[int, "str"]:
        cap = self.__makeScreenFromWind()
        arr, ones = self.__convertTo1DArray(cap)
        new_point = arr
        wep_str = knn.multiThreadfindCategory(new_point, self.__WINDPIXELS, 8, ones, fixedK=1)
        return int(wep_str), self.getWindRichtung()

if __name__ == "__main__":
    CoordMan = CoordinateManager()
    GameEnv = GameEnvironment(CoordMan)
    while True:
        print(GameEnv.getSelectedWeapon())
        print(GameEnv.getWind())