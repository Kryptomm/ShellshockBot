from pyautogui import size

class Point:
    def __init__(self, x : float, y : float) -> None:
        self.__x = x
        self.__y = y
    
    def setX(self, x : float) -> None:
        self.__x = x
        
    def setY(self, y : float) -> None:
        self.__y = y
    
    def getX(self) -> float:
        return self.__x
    
    def getY(self) -> float:
        return self.__y
    
    def getPos(self) -> tuple[float, float]:
        return (self.getX(), self.getY())

class Box:
    def __init__(self, upper_x : float, upper_y : float, bottom_x : float, bottom_y : float)  -> None:
        self.__upperLeft = Point(upper_x, upper_y)
        self.__bottomRight = Point(bottom_x, bottom_y)
        
    def getUpperLeft(self) -> Point:
        return self.__upperLeft
    
    def getBottomRight(self) -> Point:
        return self.__bottomRight
    
    def getBoundaries(self) -> tuple[float, float, float, float]:
        return (self.__upperLeft.getX(), self.__upperLeft.getY(), self.__bottomRight.getX(), self.__bottomRight.getY())
    
    def getBoundariesNormalized(self, coordinateManager) -> tuple[int, int, int, int]:
        return (coordinateManager.convertFloatToWidth(self.__upperLeft.getX()),
                coordinateManager.convertFloatToHeigth(self.__upperLeft.getY()),
                coordinateManager.convertFloatToWidth(self.__bottomRight.getX()),
                coordinateManager.convertFloatToHeigth(self.__bottomRight.getY()))
        
    
    def isPointInBoundaries(self, point : Point) -> bool:
        x, y = point.getPos()
        x1, y1 = self.__upperLeft.getPos()
        x2, y2 = self.__bottomRight.getPos()

        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            return True
        else:
            return False

class CoordinateManager:
    def __init__(self) -> None:
        self.__screenWidth, self.__screenHeigth = size()
        
        self.READY_BUTTON       = Box(0.613021,  0.881481,  0.8375,    0.912963)
        self.XP_FIELD           = Box(0.1625,    0.111111,  0.229167,  0.138889)
        self.WIND_FIELD         = Box(0.492708,  0.071296,  0.506771,  0.087963)
        self.WIND_FIELD_RIGHT   = Box(0.513021,  0.068519,  0.520833,  0.086111)
        self.WIND_FIELD_LEFT    = Box(0.478646,  0.068519,  0.486458,  0.086111)
        self.WEAPON_FIELD       = Box(0.371354,  0.961111,  0.494792,  0.985185)
        self.SHOOTLINE_FIELD    = Box(-0.015625, -0.277778, 0.015625,  0.018519)
        self.GAME_FIELD         = Box(0,         0,          1,         0.851852)
        self.TANK1BOX           = Box(0.260417,  0,          0.427083,  1)
        self.TANK2BOX           = Box(0.572917,  0,          0.6875,    1)
        
        self.RADIUS             = 0.178646 #dependent from width of the screen
        self.RESETANGLERADIUS   = 0.15625  #dependent from width of the screen
        
    def getScreenWidth(self) -> int:
        return self.__screenWidth
    
    def getScreenHeigth(self) -> int:
        return self.__screenHeigth
    
    def convertFloatToWidth(self, normalizedNumber : float) -> int:
        return round(normalizedNumber * self.__screenWidth)
    
    def convertFloatToHeigth(self, normalizedNumber : float) -> int:
        return round(normalizedNumber * self.__screenHeigth)
    
    def convertWidthToFloat(self, width : int) -> float:
        return width / self.__screenWidth
    
    def convertHeigthToFloat(self, heigth : int) -> float:
        return heigth / self.__screenHeigth
    
    def convertPointToCoordinate(self, normalizedPoint : Point) -> tuple[int, int]:
        return (self.convertFloatToWidth(normalizedPoint.getX()), self.convertFloatToWidth(normalizedPoint.getY()))
    


if __name__ == "__main__":
    b = Box(0.2, 0,  0.5, 1)
    p = Point(0.6,0.5)
    print(b.isPointInBoundaries(p))