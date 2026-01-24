import sys
import os
import tkinter as tk
from app.app import App
from config.load_dataset import get_dataset

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python main.py <dataset>")

    dataset_name = sys.argv[1]
    config_path = os.path.join("config", f"{dataset_name}.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config not found: {config_path}")

    dataset = get_dataset(config_path)
    root = tk.Tk()
    App(root, dataset)
    root.mainloop()

if __name__ == "__main__":
    main()