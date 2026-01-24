import sys
import os
import tkinter as tk
from app.app import App
from config.load_dataset import get_dataset

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/config.json"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config not found: {config_path}")

    dataset = get_dataset(config_path)
    root = tk.Tk()
    App(root, dataset)
    root.mainloop()

if __name__ == "__main__":
    main()