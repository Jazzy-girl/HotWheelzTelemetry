import tkinter as tk
from tkinter import PhotoImage
import random
import PIL.Image, PIL.ImageTk

class Speedometer:
    def __init__(self, parent, width=400, height=400, radius=150):
        # Transparent canvas (no background color)
        self.canvas = tk.Canvas(parent, width=width, height=height, bg="systemTransparent", bd=0, highlightthickness=0)
        self.canvas.place(x=200, y=40)  # Position the speedometer manually
        
        self.width = width
        self.height = height
        self.radius = radius
        self.center = (width // 2, height // 2)  # center of the canvas
        self.current_speed = 0  # Starting speed
        self.target_speed = 0  # Target speed (for random value)
        
        # Draw the circular background (outer circle) with no outline
        self.canvas.create_oval(self.center[0] - self.radius, self.center[1] - self.radius, 
                                self.center[0] + self.radius, self.center[1] + self.radius, outline="systemTransparent", width=0)
        
        # Draw the center hole (inner circle) with transparent outline (effectively invisible)
        self.canvas.create_oval(self.center[0] - self.radius // 2, self.center[1] - self.radius // 2, 
                                self.center[0] + self.radius // 2, self.center[1] + self.radius // 2, 
                                fill="systemTransparent", outline="systemTransparent")  # Inner circle to keep the middle part clean
        
        # Initialize the arc (speed arc starts from 0)
        self.arc = None


    def draw_speed(self, speed):
        # Limit the speed between 0 and 180
        speed = max(0, min(speed, 180))
        
        # Calculate the angle of the arc. 180 km/h corresponds to 180 degrees.
        angle = (speed / 180) * 180  # Speed from 0 to 180 maps to an angle from 0 to 180
        
        # Clear any previous arc (this ensures smooth animation)
        if self.arc:
            self.canvas.delete(self.arc)
        
        # Draw the new arc (speed) in the range from 0 to 180 degrees
        self.arc = self.canvas.create_arc(self.center[0] - self.radius, self.center[1] - self.radius, 
                                           self.center[0] + self.radius, self.center[1] + self.radius, 
                                           start=90, extent=-angle, width=20, outline="white", style="arc")
    
    def update_speed(self):
        # Generate a random target speed between 0 and 180
        self.target_speed = random.randint(0, 180)

        # Smooth animation: gradually update the speed from the current to the new random speed
        def animate():
            if self.current_speed < self.target_speed:
                self.current_speed += 1  # Increase the speed gradually
                self.draw_speed(self.current_speed)  # Redraw the speedometer with new speed
                self.canvas.after(10, animate)  # Continue the animation after 10ms
            elif self.current_speed > self.target_speed:
                self.current_speed -= 1  # Decrease the speed gradually
                self.draw_speed(self.current_speed)  # Redraw the speedometer with new speed
                self.canvas.after(10, animate)  # Continue the animation after 10ms

        animate()
        self.canvas.after(2000, self.update_speed)

def create_display_window():
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Car Monitoring System")
    root.geometry("800x480")  # Set the window size

    # Load the background image (use your image path)
    bg_image = PIL.Image.open("/path/to/your/background-image.jpg")  # Replace with your background image
    bg_image = bg_image.resize((800, 480))  # Resize to window size

    # Convert image to PhotoImage to display in Tkinter
    bg_image_tk = PIL.ImageTk.PhotoImage(bg_image)

    # Create a label to hold the background image
    bg_label = tk.Label(root, image=bg_image_tk)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Ensure it takes up the whole screen

    # Create an instance of the Speedometer class (with transparent background for the graph)
    speedometer = Speedometer(root, width=200, height=200)
    speedometer.update_speed() 
    
    root.mainloop()

if __name__ == "__main__":
    create_display_window()
