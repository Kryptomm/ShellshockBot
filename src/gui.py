# Import
import customtkinter
import customtkinter as ctk
from tkinter import *
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
    """calculate app size"""
    ratio = 16 / 9
    app_height = monitor_height
    app_width = int(round(monitor_height * ratio))
    print(f"Window information: width={app_width}px, height={app_height}px")
    return app_width, app_height
    

class App(ctk.CTk):
    def __init__(self, app_width=None, app_height=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("ShellShock Bot GUI")
        self.geometry(f"{app_width}x{app_height}")

        def create_bordered_frame(parent, relx, rely, relwidth, relheight, anchor, fg_color, text):
            outer_frame = ctk.CTkFrame(parent, fg_color="black")
            outer_frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight, anchor=anchor)

            inner_frame = ctk.CTkFrame(outer_frame, fg_color="black", border_width=2)
            inner_frame.place(relx=0.5, rely=0.5, relwidth=0.99, relheight=0.98, anchor='center')

            label = ctk.CTkLabel(inner_frame, text=text, fg_color=fg_color)
            label.pack(fill="both", expand=True)

        create_bordered_frame(self,
                              relx=0.0,
                              rely=0.85,
                              relwidth=0.4,
                              relheight=0.15,
                              anchor='sw',
                              fg_color="grey25",
                              text="Text Box 1")

        create_bordered_frame(self,
                              relx=0.0,
                              rely=1.0,
                              relwidth=0.4,
                              relheight=0.15,
                              anchor='sw',
                              fg_color="grey25",
                              text="Text Box 2")

        create_bordered_frame(self,
                              relx=0.4,
                              rely=1.0,
                              relwidth=0.4,
                              relheight=0.3,
                              anchor='sw',
                              fg_color="grey25",
                              text="Text Box 3")

        create_bordered_frame(self,
                              relx=0.8,
                              rely=1.0,
                              relwidth=0.2,
                              relheight=0.15,
                              anchor='sw',
                              fg_color="grey25",
                              text="Text Box 4")

        create_bordered_frame(self,
                              relx=0.8,
                              rely=0,
                              relwidth=0.2,
                              relheight=0.85,
                              anchor='nw',
                              fg_color="grey25",
                              text="Buttons can be placed here")


if __name__ == "__main__":
    monitor_width = get_monitor_width()
    app_width, app_height = get_app_size(monitor_width)
    app = App(app_width=app_width, app_height=app_height)
    #app = App(app_width=1920, app_height=1080)
    app.mainloop()
