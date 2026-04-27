import filecmp
import os
import tempfile
import time
import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk
from typing import cast

import networkx as nx
import numpy as np
import pandas as pd
from PIL import Image, ImageTk

from ..datasets import WildlifeDataset
from .utils import convert_identity, download_file

DATA_CSV = "verification_data.csv"
SEGMENTATION_CSV = "segmentation.csv"
ANS_CSV = "answers.csv"
ANS_POS = "same"
ANS_NEG = "different"
ANS_UNK = ""
CANVAS_SIZE = 400


class App:
    def __init__(self, root: tk.Tk, dataset: WildlifeDataset, name: str) -> None:
        self.root = root
        self.root.title("Image Comparator")
        self.dataset = dataset
        self.name = name
        self.skip_filled = True

        # Check whether the dataset was downloaded
        if not self.dataset.is_downloaded():
            self.download_dataset()
            if not self.dataset.is_downloaded():
                self.root.destroy()
                return

        # Load the verification data
        if not os.path.exists(DATA_CSV):
            self.download_verification()
        df = pd.read_csv(DATA_CSV)
        assert isinstance(df.index, pd.RangeIndex)

        # Check if segmentation data exist
        _, paths = self.dataset.get_segmentation_files()
        for path in paths:
            if not os.path.exists(path):
                self.download_segmentation()
                break

        # Load the dataset
        self.dataset.load()

        # Build UI
        self.idx = 0
        self.increase = True
        self._build_ui()
        self._bind_keys()
        self._initialize_answers(df)
        self._check_answers(df)
        self._initial_load()
        self._reset_i_lr()

    def _initialize_answers(self, df):
        # Load the answer data
        if os.path.exists(ANS_CSV):
            self.answers = pd.read_csv(ANS_CSV)
            self.answers["answer"] = self.answers["answer"].astype(object)
            self.answers["time"] = self.answers["time"].astype(float)
        else:
            self.answers = df.copy()
            self.answers["answer"] = None
            self.answers["time"] = 0.0

        # Verify the segmentation data
        self.answers["index1"] = self.answers["image_id1"].apply(self.dataset.get_index_query)
        self.answers["index2"] = self.answers["image_id2"].apply(self.dataset.get_index_database)

    def _check_answers(self, df):
        # Verify the answer data
        columns1 = self.answers.columns.difference({"answer", "time", "index1", "index2"})
        columns2 = df.columns
        if set(columns1) != set(columns2) or not self.answers[columns1].equals(df[columns1]):
            messagebox.showinfo("Info", f"File {ANS_CSV} has wrong format. It may help to delete it.")
            self.close_app()

    def _initial_load(self):
        idx_null = self.answers[["index1", "index2"]].isnull()
        if idx_null.any().any():
            messagebox.showinfo("Info", "Some entries are mismatched. Try to download segmentation of dataset.")
        else:
            # Load the first couple of images
            self._initialize_skipping()
            self.load_row()

    def _actions(self) -> list[tuple[str, str | None, Callable, int, int]]:
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
            ("Toggle heads left (R)", "r", self.on_toggle_left, 0, 3),
            ("Toggle heads right (F)", "f", self.on_toggle_right, 1, 3),
            ("Reset (V)", "v", self.on_reset, 2, 3),
        ]

    def _build_ui(self) -> None:
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
        self.counter_label = ttk.Label(
            self.main_frame, textvariable=self.counter_var, font=("TkDefaultFont", 12, "bold")
        )
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
            takefocus=0,
        )
        self.text_box.pack(fill="both", expand=True)

        for text, _, action, row, col in self._actions():
            ttk.Button(self.btn_frame, text=text, command=action).grid(row=row, column=col)

    def _bind_keys(self) -> None:
        for _, key, action, _, _ in self._actions():
            if key is not None:
                self.root.bind(key, lambda e, a=action: a())

    def _elapsed_since_plot(self) -> float:
        return time.perf_counter() - self.plot_time

    def _fit_to_canvas(self, img: Image.Image) -> Image.Image:
        w, h = img.size
        scale = min(CANVAS_SIZE / w, CANVAS_SIZE / h)
        new_size = (int(w * scale), int(h * scale))
        return img.resize(new_size, Image.Resampling.LANCZOS)

    def _log_time(self) -> None:
        current = cast(float, self.answers.loc[self.idx, "time"])
        elapsed = self._elapsed_since_plot()
        self.answers.loc[self.idx, "time"] = current + elapsed
        self._save_csv()

    def _reset_time(self) -> None:
        self.plot_time = time.perf_counter()

    def _save_csv(self) -> None:
        answers_save = self.answers.drop(["index1", "index2", "identity1_convert", "identity2_convert"], axis=1)
        answers_save.to_csv(ANS_CSV, index=False)

    def _set_text(self) -> None:
        # TODO: add more information?
        self.text_box.config(state="normal")
        self.text_box.delete("1.0", "end")
        for i, (matching_part, answers_subset) in enumerate(self.answers.groupby("matching_part")):
            assert isinstance(matching_part, str)
            name = matching_part.upper()
            done = ~answers_subset["answer"].isnull()

            n = len(answers_subset)
            n_done = done.sum()

            self.text_box.insert(f"{i + 1}.0", f"{name} ({n}): done {n_done}.\n")
        self.text_box.config(state="disabled")

    def on_same(self, event=None) -> None:
        self._log_time()
        self.answer(ANS_POS)

    def on_diff(self, event=None) -> None:
        self._log_time()
        self.answer(ANS_NEG)

    def on_unknown(self, event=None) -> None:
        self._log_time()
        self.answer(ANS_UNK)

    def on_toggle_left(self, event=None) -> None:
        self._toggle("l")

    def on_toggle_right(self, event=None) -> None:
        self._toggle("r")

    def on_prev(self, event=None) -> None:
        self._log_time()
        self.prev()

    def on_next(self, event=None) -> None:
        self._log_time()
        self.next()

    def on_reset(self, event=None) -> None:
        img1, img2 = self.load_images()
        self._show_image(img1, "l")
        self._show_image(img2, "r")
        self._reset_i_lr()
    
    def download_dataset(self, event=None) -> None:
        confirm = messagebox.askyesno(
            title="Download dataset",
            message="Download may take tens of minutes. Download the dataset now? Do not close the app please. It will close automatically.",
        )
        if confirm:
            self.dataset.download_dataset()
            self.close_app()

    def next_body_part(self) -> None:
        self.skip_filled = True
        unique_parts = self.answers["matching_part"].unique()
        i = np.where(self.answers.iloc[self.idx]["matching_part"] == unique_parts)[0][0]
        i = np.mod(i + 1, len(unique_parts))
        self.idx = np.where(unique_parts[i] == self.answers["matching_part"])[0][0] - 1
        self.next()

    # TODO: handle if internet not connected
    def _download_files(self, paths: list[str], urls: list[str]) -> None:
        confirm = messagebox.askyesno(
            title="Download", message="Download the file now? Do not close the app please. It will close automatically."
        )
        if not confirm:
            return

        replaced = False
        for path, url in zip(paths, urls):
            base_name = os.path.basename(path)
            with tempfile.TemporaryDirectory() as tmpdir:
                path_tmp = os.path.join(tmpdir, base_name)
                download_file(url, path_tmp)
                if not os.path.exists(path_tmp):
                    raise RuntimeError(f"Download failed for {base_name}")
                if not (os.path.exists(path) and filecmp.cmp(path, path_tmp, shallow=False)):
                    path_dir = os.path.dirname(path)
                    if path_dir != "":
                        os.makedirs(path_dir, exist_ok=True) 
                    os.replace(path_tmp, path)
                    replaced = True
        if replaced:
            messagebox.showinfo("Info", "The file is already the newest one.")
            self._reset_time()
        else:
            self.close_app(message="The file has been downloaded. The application will now close.")

    def download_segmentation(self) -> None:
        urls, paths = self.dataset.get_segmentation_files()
        self._download_files(paths, urls)

    def download_verification(self) -> None:
        assert self.dataset.verification_url is not None
        self._download_files([DATA_CSV], [self.dataset.verification_url])

    def close_app(self, message: str = "The application will now close.") -> None:
        messagebox.showinfo("Exit", message)
        self.root.destroy()

    def _reset_i_lr(self) -> None:
        self.i_l = 0
        self.i_r = 0

    def _update_i_lr(self, n: int, position: str) -> None:
        if position == "l":
            self.i_l = (self.i_l + 1) % n
        elif position == "r":
            self.i_r = (self.i_r + 1) % n

    def _toggle(self, position):
        # TODO: "encounter1" and "encounter2" is required
        if position == "l":
            col_encounter = "encounter1"
            dataset = self.dataset.query
            i = self.i_l
        elif position == "r":
            col_encounter = "encounter2"
            dataset = self.dataset.database
            i = self.i_r
        else:
            raise ValueError("Position must be l or r.")
        assert dataset is not None

        # TODO: do not hard-code heads and encounter_id
        encounter = self.answers.iloc[self.idx][col_encounter]
        mask1 = dataset.metadata["label"] == "head"
        mask2 = dataset.metadata["encounter_id"] == encounter
        metadata_reduced = dataset.metadata[mask1 & mask2]
        metadata_reduced = metadata_reduced.sort_values("score", ascending=False)
        index = dataset.metadata.index.get_indexer(metadata_reduced.index)
        
        if len(index) > 0:
            img = dataset[index[i]]
            self._show_image(img, position)
            self._update_i_lr(len(index), position)

    def _initialize_skipping(self):
        self.answers["identity1_convert"] = convert_identity(self.answers, "identity1", "encounter1")
        self.answers["identity2_convert"] = convert_identity(self.answers, "identity2", "encounter2")        
        self._graph_init()
        self._graph_check()

    @property
    def mask_same(self):
        return self.answers["answer"] == ANS_POS

    @property
    def mask_diff(self):
        return self.answers["answer"] == ANS_NEG

    def _update_answer(self, answer_new: str) -> None:
        # TODO: the whole logic will break if A-B same, B-C different, A-C different and the user changes B-C to same
        answer_old = self.answers.loc[self.idx, "answer"]
        a = self.answers.iloc[self.idx]["identity1_convert"]
        b = self.answers.iloc[self.idx]["identity2_convert"]
        if answer_new == ANS_POS:
            # To keep the forest structure (no cycles), add only if not connected, otherwise, change answer to ""
            if not nx.has_path(self.G_same, a, b):
                self.G_same.add_edge(a, b)
            else:
                answer_new = ANS_UNK
        elif answer_old == ANS_POS:
            self.G_same.remove_edge(a, b)
        self.answers.loc[self.idx, "answer"] = answer_new

    def _graph_init(self):
        nodes = np.unique(self.answers["identity1_convert"].to_list() + self.answers["identity2_convert"].to_list())
        edges_same = self.answers.loc[self.mask_same, ["identity1_convert", "identity2_convert"]].to_numpy()

        self.G_same = nx.Graph()
        self.G_same.add_nodes_from(nodes.tolist())
        self.G_same.add_edges_from(edges_same.tolist())

    def _graph_check(self):
        if not nx.is_forest(self.G_same):
            raise ValueError("G_same must not have any cycles")
        for _, answer in self.answers[self.mask_diff].iterrows():
            if nx.has_path(self.G_same, answer["identity1_convert"], answer["identity2_convert"]):
                raise ValueError("Cluster contains both same and different.")

    def _answer_exists(self) -> bool:
        # Get the identities
        a = self.answers.iloc[self.idx]["identity1_convert"]
        b = self.answers.iloc[self.idx]["identity2_convert"]
        
        # If the identites are connected by same, it is predicted
        if nx.has_path(self.G_same, a, b):
            return True

        # Extract the components where the identities belong
        comp_a = nx.node_connected_component(self.G_same, a)
        comp_b = nx.node_connected_component(self.G_same, b)

        # Check whether identities are connected by exactly one diff
        diff_edges = self.answers.loc[self.mask_diff, ["identity1_convert", "identity2_convert"]].to_numpy()
        for u, v in diff_edges:
            if (u in comp_a and v in comp_b) or (v in comp_a and u in comp_b):
                return True

        return False

    def _answer_empty(self) -> bool:
        answer = self.answers.iloc[self.idx]["answer"]
        return pd.isnull(answer) or answer == ""
    
    def _skip_plotting(self) -> bool:
        if self.skip_filled:
            return self._answer_exists() or not self._answer_empty()
        else:
            return self._answer_exists() and self._answer_empty()

    def next_prev(self) -> None:
        if self.increase:
            self.next()
        else:
            self.prev()

    def load_image_database(self, i: int | None = None) -> Image.Image:
        assert self.dataset.database is not None
        if i is None:
            i = self.idx
        row = self.answers.iloc[i]
        img = self.dataset.database[row["index2"]]
        assert isinstance(img, Image.Image)
        return img

    def load_image_query(self, i: int | None = None) -> Image.Image:
        assert self.dataset.query is not None
        if i is None:
            i = self.idx
        row = self.answers.iloc[i]
        img = self.dataset.query[row["index1"]]
        assert isinstance(img, Image.Image)
        return img

    def load_images(self, **kwargs) -> tuple[Image.Image, Image.Image]:
        img1 = self.load_image_query(**kwargs)
        img2 = self.load_image_database(**kwargs)
        return img1, img2

    def _show_image(self, img, position):
        if position == "l":
            self.canvas_l.delete("all")
            self.tk_img_l = ImageTk.PhotoImage(self._fit_to_canvas(img))
            self.canvas_l.create_image(200, 200, image=self.tk_img_l)
        elif position == "r":
            self.canvas_r.delete("all")
            self.tk_img_r = ImageTk.PhotoImage(self._fit_to_canvas(img))
            self.canvas_r.create_image(200, 200, image=self.tk_img_r)
        else:
            raise ValueError("Position must be l or r.")
        
    def load_row(self) -> None:
        if not (0 <= self.idx < len(self.answers)):
            if self.skip_filled:
                messagebox.showinfo(
                    "Info", "All turtles were identified. Either delete some rows in answers.csv or the whole file."
                )
            self.root.destroy()
            return

        if self._skip_plotting():
            self.next_prev()
            return

        img1, img2 = self.load_images()

        if img1 is None or img2 is None:
            self.next_prev()
            return

        text = f"{self.name} image {self.idx + 1}/{len(self.answers)}"
        answer = self.answers.iloc[self.idx]["answer"]
        if not pd.isnull(answer):
            text = f"{text} - {answer.upper()}"
        self.counter_var.set(text)

        self._show_image(img1, "l")
        self._show_image(img2, "r")

        self.skip_filled = False
        self._set_text()
        self._reset_i_lr()

        self._reset_time()

    def answer(self, answer) -> None:
        self._update_answer(answer)
        self._save_csv()
        self.next()

    def next(self) -> None:
        self.increase = True
        self.idx += 1
        self.load_row()

    def prev(self) -> None:
        if self.idx > 0:
            self.increase = False
            self.idx -= 1
            self.load_row()
