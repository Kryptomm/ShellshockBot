# Import
import customtkinter
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
        self.title("ShellShock Bot GUI")
        self.geometry(f"{app_width}x{app_height}")

        label_one = ctk.CTkLabel(self,
                                 text="Text Box 1",
                                 fg_color="lightblue")
        label_one.place(relx=0.0, rely=0.85, relwidth=0.4, relheight=0.15, anchor='sw')

        label_two = ctk.CTkLabel(self,
                                 text="Text Box 2",
                                 fg_color="blue")
        label_two.place(relx=0.0, rely=1.0, relwidth=0.4, relheight=0.15, anchor='sw')

        label_three = ctk.CTkLabel(self,
                                   text="Text Box 3",
                                   fg_color="darkblue")
        label_three.place(relx=0.4, rely=1.0, relwidth=0.4, relheight=0.3, anchor='sw')

        label_four = ctk.CTkLabel(self,
                                  text="Text Box 4",
                                  fg_color="grey")
        label_four.place(relx=0.8, rely=1.0, relwidth=0.2, relheight=0.15, anchor='sw')

        label_buttons = ctk.CTkLabel(self,
                                     text="Buttons can be placed here",
                                     fg_color="red")
        label_buttons.place(relx=0.8, rely=0, relwidth=0.2, relheight=0.85, anchor='nw')


if __name__ == "__main__":
    monitor_width = get_monitor_width()
    app_width, app_height = get_app_size(monitor_width)
    #app = App(app_width=app_width, app_height=app_height)
    app = App(app_width=1920, app_height=1080)
    app.mainloop()
