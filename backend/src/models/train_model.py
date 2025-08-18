import warnings

warnings.filterwarnings("ignore")

import gzip
import os
import pickle
import pickletools

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


def save_model(filename: str, model: object):
    """
    Function saves model into pickle object.
    """
    file_path = os.path.join(ROOT_DIR, "models", filename)
    with gzip.open(file_path, "wb") as f:
        pickled = pickle.dumps(model)
        optimized_pickle = pickletools.optimize(pickled)
        f.write(optimized_pickle)


def main():
    file_path = os.path.join(ROOT_DIR, "data", "processed", "Titanic-Dataset.csv")
    df = pd.read_csv(file_path)
    features = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]
    target = "Survived"

    df = df[features + [target]].copy()
    X = df[features]

    y = df[target].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    numeric_features = ["Age", "SibSp", "Parch", "Fare"]
    categorical_features = ["Pclass", "Sex", "Embarked"]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocess = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    rf = RandomForestClassifier(
        n_estimators=200, max_depth=None, random_state=42, n_jobs=-1
    )

    model = Pipeline(steps=[("preprocess", preprocess), ("rf", rf)])

    # Train model
    model.fit(X_train, y_train)

    # Evaluate before saving
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test accuracy (before save): {acc:.3f}")
    print(classification_report(y_test, y_pred))

    # Serialize (save) the trained pipeline
    model_path = "titanic_rf.pkl.gz"
    save_model(model_path, model)
    print(f"Model saved to: {model_path}")


if __name__ == "__main__":
    main()
