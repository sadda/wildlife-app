import tkinter as tk
from tkinter import ttk
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
import os
from wildlife_datasets.datasets import TurtlesOfSMSRC
from utils import get_index

DATA_CSV = "data.csv"
ANS_CSV = "answers.csv"
ANS_POS = "same"
ANS_NEG = "diff"
ANS_UNK = "unknown"
ROOT = "data/TurtlesOfSMSRC"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Comparator")
        # TODO: the segmentation.csv file must be identical
        self.dataset = TurtlesOfSMSRC(ROOT, load_segmentation=True, img_load='bbox')

        self.df = pd.read_csv(DATA_CSV)
        assert isinstance(self.df.index, pd.RangeIndex)
        
        self.idx = 0
        self.increase = True

        if os.path.exists(ANS_CSV):
            self.answers = pd.read_csv(ANS_CSV)
        else:
            self.answers = self.df.copy()
            self.answers['answer'] = None

        self._build_ui()
        self._bind_keys()
        self.load_row()

    def _actions(self):
        return [
            ("Same (Q)", "q", self.on_same, 0, 0),
            ("Different (W)", "w", self.on_diff, 0, 1),
            ("Unknown (E)", "e", self.on_unknown, 0, 2),
            ("Show heads (R)", "r", self.show_heads, 0, 3),
            ("Previous (A)", "a", self.prev, 1, 0),
            ("Next (S)", "s", self.next, 1, 1),
        ]

    def _build_ui(self):
        self.img_frame = ttk.Frame(self.root)
        self.img_frame.pack(padx=10, pady=10)

        self.canvas_l = tk.Canvas(self.img_frame, width=400, height=400)
        self.canvas_r = tk.Canvas(self.img_frame, width=400, height=400)
        self.canvas_l.grid(row=0, column=0, padx=5)
        self.canvas_r.grid(row=0, column=1, padx=5)

        self.btn_frame = ttk.Frame(self.root)
        self.btn_frame.pack(pady=10)

        for text, _, action, row, col in self._actions():
            ttk.Button(
                self.btn_frame,
                text=text,
                command=action
            ).grid(row=row, column=col)

    def _bind_keys(self):
        for _, key, action, _, _ in self._actions():
            self.root.bind(key, lambda e, a=action: a())

    def on_same(self, event=None):
        self.answer(ANS_POS)

    def on_diff(self, event=None):
        self.answer(ANS_NEG)

    def on_unknown(self, event=None):
        self.answer(ANS_UNK)

    def on_heads(self, event=None):
        self.show_heads()

    def on_prev(self, event=None):
        self.prev()

    def on_next(self, event=None):
        self.next()

    def _load_image(self, image_id, identity=None):        
        j = get_index(self.dataset, image_id)
        if j is None:
            return None
        if identity is not None:
            if self.dataset.metadata['identity'].iloc[j] != identity:
                print(self.dataset.metadata['identity'].iloc[j], identity)
                raise ValueError('Identity is different. Segmentation.csv is probably wrong')
        return self.dataset[j]

    def _answer_exists(self, identity1, identity2):
        idx1 = (self.df['identity1'] == identity1) * (self.df['identity2'] == identity2)
        idx2 = (self.df['identity1'] == identity2) * (self.df['identity2'] == identity1)
        idx = idx1 + idx2
        ans = self.answers.loc[idx, 'answer']
        return (ans.isin([ANS_NEG, ANS_POS])).any()

    def next_prev(self):
        if self.increase:
            self.next()
        else:
            self.prev()

    def load_images(self, row):
        img1 = self._load_image(row['image_id1'], identity=row['identity1'])
        img2 = self._load_image(row['image_id2'], identity=row['identity2'])
        return img1, img2

    def load_row(self):
        self.canvas_l.delete("all")
        self.canvas_r.delete("all")

        row = self.df.iloc[self.idx]

        if self._answer_exists(row['identity1'], row['identity2']):
            self.next_prev()
            return
        
        img1, img2 = self.load_images(row)

        if img1 is None or img2 is None:
            self.next_prev()
            return

        self.tk_img1 = ImageTk.PhotoImage(img1)
        self.tk_img2 = ImageTk.PhotoImage(img2)

        self.canvas_l.create_image(200, 200, image=self.tk_img1)
        self.canvas_r.create_image(200, 200, image=self.tk_img2)

    def answer(self, answer):
        self.answers.loc[self.idx, "answer"] = answer
        self.answers.to_csv(ANS_CSV, index=False)
        self.next()

    def show_heads(self):
        # TODO: finish
        pass

    def next(self):
        self.increase = True
        if self.idx < len(self.df) - 1:
            self.idx += 1
            self.load_row()
        else:
            self.root.destroy()

    def prev(self):
        self.increase = False
        if self.idx > 0:
            self.idx -= 1
            self.load_row()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
