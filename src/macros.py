import json
import os
import keyboard
import environment, coordinateManager
from collections import deque
from pyautogui import locateOnScreen, click
from time import sleep
from threading import Thread
from pynput.keyboard import Listener

settings = None
try:
    settings = json.load(open("settings.json", encoding='utf-8'))
except:
    settings = json.load(open(f"{os.getcwd()}/src/settings.json", encoding='utf-8'))
macros = {}

targettedWeapons = ["earthquake", "mega-quake", "shockwave", "sonic pulse", "drone", "heavy drone",
                    "health aura", "health aura+", "health aura++", "small potion", "medium potion", "large potion", "huge potion"]

coordManager = coordinateManager.CoordinateManager()
gameEnvironment = environment.GameEnvironment(coordManager)

for m in settings["macro"]: macros[m] = False

def press_key(key, timer=0):
    keyboard.press(key)
    sleep(timer)
    keyboard.release(key)

def isVisible(picture, region):
    visible = locateOnScreen(f"Images/{picture}.png", grayscale=True, confidence=0.9, region=region)
    if visible: return True
    else: return False

def overcharge():
    while True:
        sleep(1)

        if macros["overcharge"] == "exit":exit()
        if not macros["overcharge"]: continue
        
        lastFoundWeapons = deque(maxlen=4)
        currentDirection = False
        adjusted = False

        while macros["overcharge"] and not macros["overcharge"] == "exit":
            click(530,1000)
            sleep(0.25)
            
            #Solange ich noch nicht Pressen kann
            isGonnaShoot = False
            checks, maxChecks = 0, 6
            while not (isVisible("FireButton", region=(1000,900, 1420, 1100))) and not macros["overcharge"] == "exit":
                if checks >= maxChecks: continue
                
                selected_weapon = gameEnvironment.getSelectedWeapon()
                isGonnaShoot = selected_weapon[0] in targettedWeapons
                if not isGonnaShoot:
                    #In eine Richtung bewegen beim Waffen sortieren
                    if selected_weapon in lastFoundWeapons:
                        print("changing search direction")
                        currentDirection = not currentDirection
                        lastFoundWeapons.clear()
                    lastFoundWeapons.append(selected_weapon)
                    if currentDirection:
                        press_key("s")
                    else:
                        press_key("w")
                        
                checks += 1
                    
            if isGonnaShoot: 
                print("shooting")
                if not adjusted:
                    for _ in range(100):
                        press_key("down", timer=0.05)
                    press_key("up",timer=0.05)
                    adjusted = True
                gameEnvironment.pressButton(gameEnvironment.FireButton)
            else:
                print("Overcharge")
                click(493,460)
                
            if currentDirection:
                press_key("s")
            else:
                press_key("w")

def on_press(key):
    key = "{0}".format(key).replace("'","")

    if key == settings["macro"]["exit"]:
        for m in macros: macros[m] = "exit"
        exit()

    for m in settings["macro"]:
        if key == settings["macro"][m]:
            macros[m] = not macros[m]
            if macros[m]: print(f"{m} activated")
            else: print(f"{m} deactivated")

def on_release(key):
    pass

if __name__ == "__main__":
    with Listener(on_press=on_press, on_release=on_release) as listener:
        Thread(target=overcharge).start()
        print("Makro Ready")
        listener.join()