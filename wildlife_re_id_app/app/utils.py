import requests

import pandas as pd


def convert_identity(answers: pd.DataFrame, col_identity: str, col_encounter: str | None = None) -> pd.Series:
    mask = answers[col_identity] == "unknown"    
    if not mask.any():
        return answers[col_identity]
    if col_encounter not in answers.columns:
        raise ValueError(f"Column {col_encounter} must be in answers if there are unknown identities")    
    identity = answers[col_identity].copy().astype(str)
    identity[mask] = "unknown" + "_" + answers.loc[mask, col_encounter].astype(str)
    return identity

def download_file(url: str, output_path: str) -> None:
    r = requests.get(url, allow_redirects=True)
    r.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(r.content)
