from typing import Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib


def load_data() -> Tuple[list, list]:
    """
    Loads the dataset used for training the model.

    Returns:
        Tuple[list, list]: The loaded data and their labels.
    """
    categories = ['sci.space', 'talk.politics.misc']  # Example categories for demonstration
    data = fetch_20newsgroups(subset='all', categories=categories, shuffle=True, random_state=42)
    return data.data, data.target


def create_and_train_model(X_train: list, y_train: list) -> Pipeline:
    """
    Creates, trains, and returns a machine learning model for spam detection.

    Args:
        X_train (list): The training data.
        y_train (list): The labels for the training data.

    Returns:
        Pipeline: The trained machine learning model.
    """
    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    model.fit(X_train, y_train)
    return model


def evaluate_model(model: Pipeline, X_test: list, y_test: list) -> None:
    """
    Evaluates the model's performance on the test set.

    Args:
        model (Pipeline): The trained machine learning model.
        X_test (list): The test data.
        y_test (list): The labels for the test data.
    """
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))


def save_model(model: Pipeline, filename: str = 'spam_classifier.joblib') -> None:
    """
    Saves the trained model to a file.

    Args:
        model (Pipeline): The trained machine learning model.
        filename (str): The name of the file to save the model. Defaults to 'spam_classifier.joblib'.
    """
    joblib.dump(model, filename)


def create_model():
    """
    Main function to execute the model training, evaluation, and saving process.
    """
    # Load and split the dataset
    data, target = load_data()
    X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=0.25, random_state=42)

    # Create, train, and evaluate the model
    model = create_and_train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)

    # Save the model
    save_model(model)


if __name__ == "__main__":
    create_model()
