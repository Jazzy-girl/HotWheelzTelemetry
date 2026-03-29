from tkinter import *

root=Tk()

Grid.rowconfigure(root, 0, weight=1)
Grid.columnconfigure(root, 0, weight=1)
Grid.rowconfigure(root, 1, weight=1)
Grid.columnconfigure(root, 1, weight=1)

buttonRed = Button(root, bg="red")
buttonGreen =Button(root, bg="green")
buttonBlue = Button(root, bg="blue")
buttonYellow = Button(root, bg="yellow")

buttonRed.grid(row=0, column=0, sticky='NSEW')
buttonGreen.grid(row=0, column=1, sticky='NSEW')
buttonBlue.grid(row= 1, column = 0, sticky='NSEW')
buttonYellow.grid(row=1, column=1, sticky='NSEW')

root.mainloop()