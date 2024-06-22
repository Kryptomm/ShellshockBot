# Import
import customtkinter as ctk
from screeninfo import get_monitors

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Initialize variables
monitor_height: int = 0


def get_monitor_width():
    """get height of monitor in pixels"""
    global monitor_height
    for monitor in get_monitors():
        if monitor.is_primary:
            monitor_height = int(monitor.height)
            break
    return monitor_height


def get_app_size(monitor_height):
    ratio = 16 / 9
    app_height = monitor_height
    app_width = int(round(monitor_height * ratio))
    print(f"Window information: width={app_width}px, height={app_height}px")
    return app_width, app_height
    

class App(ctk.CTk):
    def __init__(self, app_width=None, app_height=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Shellshock")
        self.geometry(f"{app_width}x{app_height}")


if __name__ == "__main__":
    monitor_width = get_monitor_width()
    app_width, app_height = get_app_size(monitor_width)
    app = App(app_width=app_width, app_height=app_height)
    app.mainloop()
