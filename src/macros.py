import json
from pywinauto.application import Application
from pyautogui import locateOnScreen, click
from time import sleep
from threading import Thread
from pynput.keyboard import Listener

settings = json.load(open("settings.json", encoding='utf-8'))
macros = {}

for m in settings["macro"]: macros[m] = False

def isVisible(picture, region):
    visible = locateOnScreen(f"Images/{picture}.png", grayscale=True, confidence=0.9, region=region)
    if visible: return True
    else: return False

def overcharge():
    while True:
        sleep(1)

        if macros["overcharge"] == "exit":exit()
        if not macros["overcharge"]: continue

        while macros["overcharge"] and not macros["overcharge"] == "exit":
            click(530,1000)
            sleep(0.25)
            
            while not (isVisible("FireButton", region=(1000,900, 1420, 1100))) and not macros["overcharge"] == "exit": pass
            print("overcharge: Klick")
            
            click(493,460)

def fortify():
    while True:
        sleep(1)

        if macros["fortify"] == "exit": exit()
        if not macros["fortify"]: continue

        while macros["fortify"] and not macros["fortify"] == "exit":
            click(530,1000)
            sleep(0.25)
            
            while not (isVisible("FireButton", region=(1000,900, 1420, 1100))) and not macros["overcharge"] == "exit": pass
            print("fortify: Klick")
            
            click(474,504)

def on_press(key):
    print("Key pressed: {0}".format(key))
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
        Thread(target=fortify).start()
        Thread(target=overcharge).start()
        print("Makro Ready")
        listener.join()