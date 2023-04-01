from pywinauto.application import Application
import pywinauto.keyboard

coords = coords=(177,500)
game = "ShellShock Live"

app = Application().connect(title_re=game)

print("Controlling")
app.top_window().send_keystrokes(" ")
