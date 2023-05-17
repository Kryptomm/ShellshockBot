from time import sleep
from pyautogui import click

import colors
from definitions import RULES
from environment import GameEnvironment
from coordinateManager import CoordinateManager
from tank import Tank, friendlyTank

def gameLoop(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    myTank = friendlyTank(colors.FRIENDLY_TANK, coordManager, gameEnvironment)
    enemyTank = Tank(colors.ENEMY_TANK, coordManager)
    
    sleep(8)
    myTank.getAverageCoordinatesBreadth()
    enemyTank.getAverageCoordinatesBreadth()
    
    if myTank.getXCoordinate() <= enemyTank.getXCoordinate():
        myTank.BOUNDARIES = coordManager.TANK1BOX
        enemyTank.BOUNDARIES = coordManager.TANK2BOX
    else:
        myTank.BOUNDARIES = coordManager.TANK2BOX
        enemyTank.BOUNDARIES = coordManager.TANK1BOX
    
    while True:
        while not gameEnvironment.isMyTurn():
            if gameEnvironment.inLoadingScreen(): click(1013, 1050)
            if gameEnvironment.inLobby(): return
            
        gameEnvironment.isShootingState = True
        
        myTank.getAverageCoordinatesBreadth()
        enemyTank.getAverageCoordinatesBreadth()
        
        if myTank.move():
            myTank.getAverageCoordinatesBreadth()
        
        myTank.shoot(enemyTank)
        gameEnvironment.isShootingState = False

def lobbyWrapperLoop(coordManager : CoordinateManager, gameEnvironment : GameEnvironment) -> None:
    while True:
        gameEnvironment.pressButton(gameEnvironment.ReadyButton)
        
        while gameEnvironment.inLobby():
            sleep(0.1)
        
        gameEnvironment.inLobbyState = False
        gameLoop(coordManager, gameEnvironment)
        gameEnvironment.inLobbyState = True

def main() -> None:
    print(RULES)
    
    coordManager = CoordinateManager()
    gameEnvironment = GameEnvironment(coordManager)
    
    if gameEnvironment.inLobby() == False:
        print("Starte von der Lobby aus!")
        return

    lobbyWrapperLoop(coordManager, gameEnvironment)

if __name__ == "__main__":
    wait = 1
    for x in range(wait):
        print(f"starting in {wait-x}...")
        sleep(1)
    main()