import sys
import os
import tkinter as tk
from wildlife_re_id_app.app import App
from config.load_dataset import get_dataset

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config"
    config_path = os.path.join('config', f'{config_path}.json')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config not found: {config_path}")    

    dataset, name = get_dataset(config_path)
    root = tk.Tk()
    App(root, dataset, name)
    root.mainloop()

if __name__ == "__main__":
    main()