from pyautogui import size

class Point:
    def __init__(self, x : float, y : float) -> None:
        """a simple class for a 2D Point

        Args:
            x (float): x coordinate
            y (float): y coordinate
        """        
        self.__x = x
        self.__y = y
    
    def setX(self, x : float) -> None:
        """sets the x coordinate

        Args:
            x (float): x coordinate
        """
        self.__x = x
        
    def setY(self, y : float) -> None:
        """sets the y coordinate

        Args:
            y (float): y coordinate
        """
        self.__y = y
    
    def getX(self) -> float:
        """getter fot the x Coordinate

        Returns:
            float: x coordinate
        """
        return self.__x
    
    def getY(self) -> float:
        """getter fot the y Coordinate

        Returns:
            float: y coordinate
        """
        return self.__y
    
    def getPos(self) -> tuple[float, float]:
        """getter for both position as a vector

        Returns:
            tuple[float, float]: returns x,y as (x,y)
        """
        return (self.getX(), self.getY())
    
    def __repr__(self) -> str:
        return f"x:{self.getX()}, y:{self.getY()}"

    def __call__(self) -> tuple[float, float]:
        """Returns x and y as a tuple when called like p = Point(), x,y = p()

        Returns:
            tuple[float, float]: returns x and y as a tuple
        """
        return self.__x, self.__y

    
class Box:
    def __init__(self, upper_x : float, upper_y : float, bottom_x : float, bottom_y : float)  -> None:
        """a simple class for a 2D box

        Args:
            upper_x (float): x coordinate of upper left Point
            upper_y (float): y coordinate of upper left Point
            bottom_x (float): x coordinate of bottom right Point
            bottom_y (float): y coordinate of bottom right Point
        """
        self.__upperLeft = Point(upper_x, upper_y)
        self.__bottomRight = Point(bottom_x, bottom_y)
        
    def getUpperLeft(self) -> Point:
        """gets upper left Point

        Returns:
            Point: point class of upper left Point boundarie
        """
        return self.__upperLeft
    
    def getBottomRight(self) -> Point:
        """gets bottom right Point

        Returns:
            Point: point class of bottom right Point boundarie
        """
        return self.__bottomRight
    
    def getBoundaries(self) -> tuple[float, float, float, float]:
        """get all boundaries at once

        Returns:
            tuple[float, float, float, float]: _description_
        """
        return (self.__upperLeft.getX(), self.__upperLeft.getY(), self.__bottomRight.getX(), self.__bottomRight.getY())
    
    def getBoundariesNormalized(self, coordinateManager) -> tuple[int, int, int, int]:
        """get the boundaries normalized to the screen resolution
        perfect for screenshots

        Args:
            coordinateManager (_type_): initialized CoordinateManager class

        Returns:
            tuple[int, int, int, int]: returns as (upperx,uppery,bottomx,bottomy)
        """
        return (coordinateManager.convertFloatToWidth(self.__upperLeft.getX()),
                coordinateManager.convertFloatToHeigth(self.__upperLeft.getY()),
                coordinateManager.convertFloatToWidth(self.__bottomRight.getX()),
                coordinateManager.convertFloatToHeigth(self.__bottomRight.getY()))
        
    
    def isPointInBoundaries(self, point : Point) -> bool:
        """checks if a point is in the given boundaries only based on their values
        will not convert it automatically to relative coordinates if they arent already

        Args:
            point (Point): a point to check if it is in the box

        Returns:
            bool: True if it is in the box
        """
        x, y = point.getPos()
        x1, y1 = self.__upperLeft.getPos()
        x2, y2 = self.__bottomRight.getPos()

        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            return True
        else:
            return False
        
    def __repr__(self) -> str:
        return f"{self.__upperLeft} | {self.__bottomRight}"

class CoordinateManager:
    def __init__(self) -> None:
        """A class where all needed coordinates are already preset
        """
        self.__screenWidth, self.__screenHeigth = size()
        
        self.READY_BUTTON       = Box(0.582813,  0.789815,  0.854167,  0.999074)
        self.FIRE_BUTTON        = Box(0.534375,  0.865741,  0.735417,  0.991667)
        
        self.WIND_FIELD         = Box(0.492708,  0.071296,  0.506771,  0.087963)
        self.WIND_FIELD_RIGHT   = Box(0.513021,  0.068519,  0.520833,  0.086111)
        self.WIND_FIELD_LEFT    = Box(0.478646,  0.068519,  0.486458,  0.086111)
        
        self.WEAPON_FIELD       = Box(0.371354,  0.961111,  0.494792,  0.985185)
        self.SHOOTLINE_FIELD    = Box(-0.015625, -0.277778, 0.015625,  0.018519)
        self.GAME_FIELD         = Box(0,         0,         1,         0.851852)
        
        self.TANK1BOX           = Box(0.260417,  -1,        0.364583,  2)
        self.TANK2BOX           = Box(0.635417,  -1,        0.739583,  2)
        self.SAMETANKBOX        = Box(-0.02,      -0.02,    0.02,    0.02)
        
        self.X2                 = Box(0,         0,         1,         0.851852)
        
        self.RADIUS             = 0.178646 #dependent from width of the screen
        self.RESETANGLERADIUS   = 0.15625  #dependent from width of the screen
        
    def getScreenWidth(self) -> int:
        """getter for the screen width

        Returns:
            int: return screen width in absolute units
        """
        return self.__screenWidth
    
    def getScreenHeigth(self) -> int:
        """getter for the screen heigth

        Returns:
            int: return screen heigth in absolute units
        """
        return self.__screenHeigth
    
    def convertFloatToWidth(self, normalizedNumber : float) -> int:
        """converts a float number to an absolute number of width

        Args:
            normalizedNumber (float): a relative coordinate on the screen

        Returns:
            int: absolute width coordinate on the screen
        """
        return round(normalizedNumber * self.__screenWidth)
    
    def convertFloatToHeigth(self, normalizedNumber : float) -> int:
        """converts a float number to an absolute number of heigth

        Args:
            normalizedNumber (float): a relative coordinate on the screen

        Returns:
            int: absolute heigth coordinate on the screen
        """
        return round(normalizedNumber * self.__screenHeigth)
    
    def convertWidthToFloat(self, width : int) -> float:
        """converts an absolute number to a relative number

        Args:
            width (int): absolute position on the screen

        Returns:
            float: relative width on the screen
        """
        return width / self.__screenWidth
    
    def convertHeigthToFloat(self, heigth : int) -> float:
        """converts an absolute number to a relative number

        Args:
            heigth (int): absolute position on the screen

        Returns:
            float: relative heigth on the screen
        """
        return heigth / self.__screenHeigth
    
    def convertPointToCoordinate(self, normalizedPoint : Point) -> tuple[int, int]:
        """converts a point of relative coordinates to a tuple of screen coordinates

        Args:
            normalizedPoint (Point): gets a point of the class Point

        Returns:
            tuple[int, int]: a tuple of absolute coordinates on the screen.
        """
        return (self.convertFloatToWidth(normalizedPoint.getX()), self.convertFloatToWidth(normalizedPoint.getY()))
    


if __name__ == "__main__":
    CM = CoordinateManager()
    
    p = Point(0.3,0.5)
    
    print(CM.TANK1BOX.isPointInBoundaries(p))