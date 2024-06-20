import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import time

class ContinuousApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Continuous Method GUI with Image")
        self.geometry("400x400")

        self.label = ctk.CTkLabel(self, text="This method runs continuously", width=300, height=40)
        self.label.pack(pady=20)

        # Create a canvas to display the image
        self.canvas = ctk.CTkCanvas(self, width=200, height=200)
        self.canvas.pack(pady=20)

        self.start_time = time.time()

        # Start the continuous method
        self.continuous_method()

    def generate_image(self):
        # Create an image with PIL
        image = Image.new('RGB', (200, 200), color='white')
        draw = ImageDraw.Draw(image)
        elapsed_time = time.time() - self.start_time
        draw.text((10, 90), f"{elapsed_time:.2f} s", fill='black')
        return image

    def continuous_method(self):
        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time
        self.label.configure(text=f"Running for {elapsed_time:.2f} seconds")

        # Get the PIL image
        image = self.generate_image()
        
        # Convert PIL image to ImageTk
        self.tk_image = ImageTk.PhotoImage(image)
        
        # Update the canvas with the new image
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)

        # Schedule this method to run again after 1000ms (1 second)
        self.after(1000, self.continuous_method)

if __name__ == "__main__":
    app = ContinuousApp()
    app.mainloop()
