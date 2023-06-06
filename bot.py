from time import sleep
from pyautogui import click, FailSafeException

import colors
import globals
import os
import glob
import visualizer
import colorama
from colorama import Fore, Back, Style
from environment import GameEnvironment
from coordinateManager import CoordinateManager, Box
from tank import Tank, friendlyTank
from botThreads import initThreads
from decorators import timeit

@timeit("Play Game")
def gameLoop(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    """Runs as long as one game is going. Automatically assigns tanks to given boxes,
    shoots the friendlyTank and moves it.
    sends you back to the lobby and fast forwards the loading screen.

    Args:
        coordManager (CoordinateManager): initialized coordinateManager class
        gameEnvironment (GameEnvironment): initialized GameEnvironment class
    """    
    #initialize Tanks
    myTank = friendlyTank(colors.FRIENDLY_TANK, coordManager, gameEnvironment)
    enemyTank = Tank(colors.ENEMY_TANK, coordManager)
    
    #Wait until screen is fully there
    sleep(8)
    
    #Search for the first time
    myTank.getCoordinatesBrute()
    hideRegion = Box(myTank.getXCoordinate() - 0.05 , myTank.getYCoordinate() - 0.05 - 0.06, myTank.getXCoordinate() + 0.05, myTank.getYCoordinate() + 0.05 - 0.06)
    enemyTank.getCoordinatesBrute(hideRegions = [hideRegion])
    
    while True:
        while not gameEnvironment.isMyTurn():
            if gameEnvironment.inLoadingScreen(): click(coordManager.convertFloatToWidth(0.527604), coordManager.convertFloatToHeigth(0.9722222))
            if gameEnvironment.inLobby(): return
            
        gameEnvironment.isShootingState = True
        
        if not myTank.isInSameSpot():
            myTank.getCoordinatesBreadth()
        print(myTank)
        
        if not enemyTank.isInSameSpot():
            hideRegion = Box(myTank.getXCoordinate() - 0.05 , myTank.getYCoordinate() - 0.05 - 0.06, myTank.getXCoordinate() + 0.05, myTank.getYCoordinate() + 0.05 - 0.06)
            enemyTank.getCoordinatesBreadth(hideRegions = [hideRegion])
        print(enemyTank)
        
        if myTank.getXCoordinate() <= enemyTank.getXCoordinate():
            myTank.BOUNDARIES = coordManager.TANK1BOX
            enemyTank.BOUNDARIES = coordManager.TANK2BOX
        else:
            myTank.BOUNDARIES = coordManager.TANK2BOX
            enemyTank.BOUNDARIES = coordManager.TANK1BOX
            
        try:
            if myTank.move():
                myTank.getCoordinatesBreadth()
        except FailSafeException:
            pass
        
        visualizer.createImage(coordManager)
        myTank.shoot(enemyTank)
        gameEnvironment.isShootingState = False
        visualizer.paintPixels(myTank.getPosition()(), 15, colors.FRIENDLY_TANK, coordManager)
        visualizer.paintPixels(enemyTank.getPosition()(), 15, colors.ENEMY_TANK, coordManager)
        visualizer.saveImage()

def lobbyWrapperLoop(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    """Takes control over everything that is happening in the lobby as pushing ready and waiting there until the game started

    Args:
        coordManager (CoordinateManager): initialized coordinateManager class
        gameEnvironment (GameEnvironment): initialized GameEnvironment class
    """
    roundsPlayed = 0
    while True:
        gameEnvironment.pressButton(gameEnvironment.ReadyButton)
        
        while gameEnvironment.inLobby():
            sleep(0.1)
        
        gameEnvironment.inLobbyState = False
        gameLoop(coordManager, gameEnvironment)
        roundsPlayed += 1
        print(f"Rounds already played: {roundsPlayed}")
        gameEnvironment.inLobbyState = True

def main() -> None:
    """Initializes everything and starts up the bot
    """
    coordManager = CoordinateManager()
    
    png_files = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)), "*.png"))
    for file_path in png_files:
        os.remove(file_path)
        

    print(globals.RULES)
    
    gameEnvironment = GameEnvironment(coordManager)
    
    initThreads(coordManager, gameEnvironment)
    
    colorama.init()
    globals.initializeGlobals()
    if globals.CREATE_PICTURE:
        visualizer.createImage(coordManager)
        visualizer.saveImage()
    
    if gameEnvironment.inLobby() == False and not globals.DEBUG:
        print("Starte von der Lobby aus!")
        return

    lobbyWrapperLoop(coordManager, gameEnvironment)

if __name__ == "__main__":
    wait = 3
    for x in range(wait):
        print(f"starting in {wait-x}...")
        sleep(1)
    main()