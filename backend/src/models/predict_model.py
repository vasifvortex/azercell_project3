import warnings

warnings.filterwarnings("ignore")

import gzip
import io
import os
import pickle
from typing import Iterable, Optional

import pandas as pd

# Root of the repo (two levels up from this file)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


def load_model(filepath: str):
    """
    Load a gzip-pickled model from disk.
    """
    with gzip.open(filepath, "rb") as f:
        p = pickle.Unpickler(f)
        clf = p.load()
    return clf


def _load_dataframe_from_bytes(
    file_content: bytes, filename: Optional[str]
) -> pd.DataFrame:
    """
    Read an uploaded file (bytes) into a DataFrame using file extension.
    Defaults to Excel if the extension is ambiguous.
    """
    name = (filename or "").lower()
    buffer = io.BytesIO(file_content)

    if name.endswith(".csv"):
        df = pd.read_csv(buffer)
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        df = pd.read_excel(buffer)
    else:
        # Fall back to Excel; FastAPI already validated extensions, this is just a guard.
        df = pd.read_excel(buffer)
    return df


def main(
    file_content: Optional[bytes] = None, filename: Optional[str] = None
) -> Iterable:
    """
    Accepts raw file bytes and an optional filename to parse CSV/Excel,
    loads the trained model, and returns predictions.
    """
    # Load input features
    if file_content:
        X_test = _load_dataframe_from_bytes(file_content, filename)
    else:
        # Fallback path for local testing
        X_test_path = os.path.join(ROOT_DIR, "data", "external", "X_test.xlsx")
        X_test = pd.read_excel(X_test_path)

    # Load model and predict
    model_path = os.path.join(ROOT_DIR, "models", "titanic_rf.pkl.gz")
    loaded_model = load_model(model_path)
    y_pred = loaded_model.predict(X_test)

    try:
        return y_pred.tolist()
    except TypeError:
        return [p for p in y_pred]


if __name__ == "__main__":
    # Quick manual test (reads default X_test.xlsx)
    preds = main()
    print(f"Generated {len(preds)} predictions")
