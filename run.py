import tkinter as tk
from app import App, TurtlesOfSMSRC

ROOT = "data/TurtlesOfSMSRC"
DATASET = TurtlesOfSMSRC(ROOT)

if __name__ == "__main__":
    root = tk.Tk()
    App(root, DATASET)
    root.mainloop()