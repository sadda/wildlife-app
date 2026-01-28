import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
import filecmp
import os
import tempfile
import time

DATA_CSV = "verification_data.csv"
SEGMENTATION_CSV = 'segmentation.csv'
ANS_CSV = "answers.csv"
ANS_POS = "same"
ANS_NEG = "different"
ANS_UNK = "unknown"
CANVAS_SIZE = 400

class App:
    def __init__(self, root, dataset, name):
        self.root = root
        self.root.title("Image Comparator")
        self.dataset = dataset
        self.name = name
        self.skip_filled = True
        
        # Check whether the dataset was downloaded
        if not dataset.is_downloaded():
            self.download_dataset()
            if not dataset.is_downloaded():
                self.root.destroy()
                return
        
        # Load the dataset
        dataset.load()
        
        # Load the verification data
        if not os.path.exists(DATA_CSV):
            dataset.download_verification(DATA_CSV)
        df = pd.read_csv(DATA_CSV)
        assert isinstance(df.index, pd.RangeIndex)

        # Load the answer data
        if os.path.exists(ANS_CSV):
            self.answers = pd.read_csv(ANS_CSV)
            self.answers['answer'] = self.answers['answer'].astype(object)
        else:
            self.answers = df.copy()
            self.answers['answer'] = None
            self.answers['time'] = 0.0

        # Set the variables
        self.idx = 0
        self.increase = True
        self._build_ui()
        self._bind_keys()

        # Verify the answer data
        columns1 = self.answers.columns.difference({'answer', 'time'})
        columns2 = df.columns
        if set(columns1) != set(columns2) or not self.answers[columns1].equals(df[columns1]):
            messagebox.showinfo('Info', f'File {ANS_CSV} has wrong format. It may help to delete it.')
            self.close_app()

        # Verify the segmentation data
        self.answers['index1'] = self.answers['image_id1'].apply(dataset.get_index)
        self.answers['index2'] = self.answers['image_id2'].apply(dataset.get_index)
        idx_null = self.answers[['index1', 'index2']].isnull()
        if idx_null.any().any():
            messagebox.showinfo('Info', 'Some entries are mismatched. Try to download segmentation of dataset.')
        else:
            # Load the first couple of images
            self._initialize_skipping()
            self.load_row()

    def _actions(self):
        return [
            ("Same (Q)", "q", self.on_same, 0, 0),
            ("Different (W)", "w", self.on_diff, 0, 1),
            ("Unknown (E)", "e", self.on_unknown, 0, 2),
            ("Previous (A)", "a", self.on_prev, 1, 0),
            ("Next (S)", "s", self.on_next, 1, 1),
            ("Next body part", None, self.next_body_part, 1, 2),
            ("Download dataset", None, self.download_dataset, 2, 0),
            ("Download segmentation", None, self.download_segmentation, 2, 1),
            ("Download verification", None, self.download_verification, 2, 2),
        ]

    def _build_ui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Image frame
        self.img_frame = ttk.Frame(self.main_frame)
        self.img_frame.pack(pady=(0, 10))

        self.canvas_l = tk.Canvas(self.img_frame, width=CANVAS_SIZE, height=CANVAS_SIZE)
        self.canvas_r = tk.Canvas(self.img_frame, width=CANVAS_SIZE, height=CANVAS_SIZE)
        self.canvas_l.grid(row=0, column=0, padx=5)
        self.canvas_r.grid(row=0, column=1, padx=5)

        # Counter frame
        self.counter_var = tk.StringVar()
        self.counter_label = ttk.Label(self.main_frame, textvariable=self.counter_var, font=("TkDefaultFont", 12, "bold"))
        self.counter_label.pack(pady=(0, 10))

        # Bottom area
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill="both", expand=True)

        # Buttons (left)
        self.btn_frame = ttk.Frame(self.bottom_frame)
        self.btn_frame.grid(row=0, column=0, sticky="nw")

        # Text (right)
        bg = self.root.cget("background")
        self.text_frame = tk.Frame(self.bottom_frame, bg=bg)
        self.text_frame.grid(row=0, column=1, sticky="n", padx=(20, 0))
        self.text_box = tk.Text(
            self.text_frame,
            width=60,
            height=10,
            wrap="word",
            bg=bg,
            relief="flat",
            highlightthickness=0,
            state="disabled",
            takefocus=0
        )
        self.text_box.pack(fill="both", expand=True)

        for text, _, action, row, col in self._actions():
            ttk.Button(
                self.btn_frame,
                text=text,
                command=action
            ).grid(row=row, column=col)

    def _bind_keys(self):
        for _, key, action, _, _ in self._actions():
            if key is not None:
                self.root.bind(key, lambda e, a=action: a())

    def _elapsed_since_plot(self):
        return time.perf_counter() - self.plot_time

    def _fit_to_canvas(self, img):
        w, h = img.size
        scale = min(CANVAS_SIZE / w, CANVAS_SIZE / h)
        new_size = (int(w * scale), int(h * scale))
        return img.resize(new_size, Image.LANCZOS)

    def _initialize_skipping(self):
        idx = self.idx
        self.answers['skipping'] = False
        for i in range(len(self.answers)):
            self.idx = i
            self._update_skipping()
        self.idx = idx

    def _log_time(self):
        self.answers.loc[self.idx, "time"] += self._elapsed_since_plot()
        self._save_csv()

    def _reset_time(self):
        self.plot_time = time.perf_counter()

    def _save_csv(self):
        answers_save = self.answers.drop(['index1', 'index2', 'skipping'], axis=1)
        answers_save.to_csv(ANS_CSV, index=False)

    def _set_text(self):
        self.text_box.config(state='normal')
        self.text_box.delete('1.0', 'end')
        for i, (matching_part, answers_subset) in enumerate(self.answers.groupby('matching_part')):
            name = matching_part.upper()
            done = (~answers_subset['answer'].isnull())
            skipping = answers_subset['skipping']

            n = len(answers_subset)
            n_done = done.sum()
            n_skipping = (skipping * (~done)).sum()

            self.text_box.insert(
                f'{i+1}.0', 
                f'{name} ({n}): done {n_done}, remaining {n-n_done-n_skipping}.\n'
            )
        self.text_box.config(state='disabled')

    def _update_skipping(self):
        answers_subset = self._answer_exists()
        self.answers.loc[answers_subset.index, 'skipping'] = answers_subset.any()
        
    def on_same(self, event=None):
        self._log_time()
        self.answer(ANS_POS)

    def on_diff(self, event=None):
        self._log_time()
        self.answer(ANS_NEG)

    def on_unknown(self, event=None):
        self._log_time()
        self.answer(ANS_UNK)

    def on_prev(self, event=None):
        self._log_time()
        self.prev()

    def on_next(self, event=None):
        self._log_time()
        self.next()

    def download_dataset(self, event=None):
        confirm = messagebox.askyesno(
            title="Download dataset",
            message="Download may take tens of minutes. Download the dataset now? Do not close the app please. It will close automatically."
        )
        if confirm:
            self.dataset.download_dataset()
            self.close_app()

    def next_body_part(self):
        self.skip_filled = True
        unique_parts = self.answers['matching_part'].unique()
        i = np.where(self.answers.iloc[self.idx]['matching_part'] == unique_parts)[0][0]
        i = np.mod(i + 1, len(unique_parts))
        self.idx = np.where(unique_parts[i] == self.answers['matching_part'])[0][0] - 1
        self.next()
        # TODO: handle if internet not connected

    def _download_file(self, path_new, download_fun):
        confirm = messagebox.askyesno(
            title=f"Download",
            message=f"Download the file now? Do not close the app please. It will close automatically."
        )
        if not confirm:
            return 
        
        base_name = os.path.basename(path_new)
        with tempfile.TemporaryDirectory() as tmpdir:
            path_tmp = os.path.join(tmpdir, base_name)
            download_fun(path_tmp)
            if not os.path.exists(path_tmp):
                raise RuntimeError(f'Download failed for {base_name}')
            if os.path.exists(path_new) and filecmp.cmp(path_new, path_tmp, shallow=False):
                messagebox.showinfo('Info', f'The file is already the newest one.')
                self._reset_time()
            else:
                os.replace(path_tmp, path_new)
                self.close_app(message=f'The file has been downloaded. The application will now close.')

    def download_segmentation(self):
        self._download_file(os.path.join(self.dataset.root, SEGMENTATION_CSV), self.dataset.download_segmentation)

    def download_verification(self):
        self._download_file(DATA_CSV, self.dataset.download_verification)

    def close_app(self, message="The application will now close."):
        messagebox.showinfo("Exit", message)
        self.root.destroy()

    def _answer_subset(self, col1, col2, value1, value2):
        idx1 = (self.answers[col1] == value1) * (self.answers[col2] == value2)
        idx2 = (self.answers[col1] == value2) * (self.answers[col2] == value1)
        idx = idx1 | idx2
        return self.answers.loc[idx, 'answer']

    def _answer_exists(self):
        answer_values = [ANS_NEG, ANS_POS]
        encounter1 = self.answers.iloc[self.idx]['encounter1']
        encounter2 = self.answers.iloc[self.idx]['encounter2']
        identity1 = self.answers.iloc[self.idx]['identity1']
        identity2 = self.answers.iloc[self.idx]['identity2']
        if identity1 == 'unknown' or identity2 == 'unknown':
            answers_subset = self._answer_subset('encounter1', 'encounter2', encounter1, encounter2)
            return answers_subset.isin(answer_values)
        else:
            answers_subset1 = self._answer_subset('identity1', 'identity2', identity1, identity2)
            answers_subset2 = self._answer_subset('encounter1', 'encounter2', encounter1, encounter2)
            idx1 = answers_subset1.isin(answer_values)
            idx2 = answers_subset2.isin(answer_values)
            return idx1 | idx2
            
    def _skip_plotting(self):
        row = self.answers.iloc[self.idx]
        if self.skip_filled:
            return row['skipping'] or not pd.isnull(row['answer'])
        else:
            return row['skipping'] and pd.isnull(row['answer'])

    def next_prev(self):
        if self.increase:
            self.next()
        else:
            self.prev()

    def load_images(self):
        row = self.answers.iloc[self.idx]
        img1 = self.dataset[row['index1']]
        img2 = self.dataset[row['index2']]
        return img1, img2

    def load_row(self):
        if not (0 <= self.idx < len(self.answers)):
            if self.skip_filled:
                messagebox.showinfo('Info', 'All turtles were identified. Either delete some rows in answers.csv or the whole file.')
            self.root.destroy()
            return

        if self._skip_plotting():
            self.next_prev()
            return
        
        img1, img2 = self.load_images()

        if img1 is None or img2 is None:
            self.next_prev()
            return

        text = f'{self.name} image {self.idx + 1}/{len(self.answers)}'
        answer = self.answers.iloc[self.idx]['answer']
        if not pd.isnull(answer):
            text = f'{text} - {answer.upper()}'
        self.counter_var.set(text)

        self.canvas_l.delete("all")
        self.canvas_r.delete("all")

        self.tk_img1 = ImageTk.PhotoImage(self._fit_to_canvas(img1))
        self.tk_img2 = ImageTk.PhotoImage(self._fit_to_canvas(img2))

        self.canvas_l.create_image(200, 200, image=self.tk_img1)
        self.canvas_r.create_image(200, 200, image=self.tk_img2)

        self.skip_filled = False
        self._set_text()

        self._reset_time()

    def answer(self, answer):
        self.answers.loc[self.idx, "answer"] = answer
        self._update_skipping()
        self._save_csv()
        self.next()

    def next(self):
        self.increase = True
        self.idx += 1
        self.load_row()

    def prev(self):
        if self.idx > 0:
            self.increase = False
            self.idx -= 1
            self.load_row()
