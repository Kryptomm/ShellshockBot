import win32api, win32con, win32gui
from time import sleep

def leftClick(hwnd, pos):
    hwnd.SendMessage(hwnd, win32con.WM_CHAR, ord("w"), 0)
    sleep(0.1)

hwnd = win32gui.FindWindow(None, "ShellShock Live")
print(hwnd)
leftClick(hwnd, (1350,950))