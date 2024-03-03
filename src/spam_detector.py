import email
import imaplib
import json
from pathlib import Path
from typing import Optional, Dict, Callable

import joblib
import pandas as pd

from ml_model import create_model


def load_model(model_path: str, log_func: Callable[[str], None]):
    """
    Attempts to load a pre-trained model from the specified path. If the model does not exist,
    it trains a new model and saves it to the same path.
    """
    if Path(model_path).is_file():
        log_func(f"Loading model from {model_path}")
        return joblib.load(model_path)
    else:
        log_func(f"Model file not found at {model_path}. Training a new model.")
        create_model()  # Ensure this function trains the model and saves it to `model_path`
        log_func(f"New model trained and saved to {model_path}")
        return joblib.load(model_path)


def print_separator(log_func: Callable[[str], None]):
    """Prints a separator for better command window visibility."""
    log_func("\n" + "-" * 50 + "\n")


def create_spam_folder(mail: imaplib.IMAP4_SSL, log_func: Callable[[str], None]) -> None:
    """
    Attempts to create a 'Spam' folder in the email account.
    """
    print_separator(log_func)
    try:
        mail.create('Spam')
        log_func("Spam folder created successfully or already exists.")
    except imaplib.IMAP4.error as e:
        log_func(f"Error creating Spam folder: {e}.")


def is_spam(email_sender: str, email_subject: str, email_body: str, model, keep_df: pd.DataFrame) -> bool:
    """
    Determines if an email is spam using a pre-trained machine learning model.

    Args:
        email_sender (str): The sender of the email.
        email_subject (str): The subject of the email.
        email_body (str): The body content of the email.
        model: The pre-trained spam detection model.
        keep_df: DataFrame housing any keyword arguments that force the model NOT to classify as spam

    Returns:
        bool: True if the email is considered spam, False otherwise.
    """
    # Check each row in the DataFrame for keywords
    for _, row in keep_df.iterrows():
        # Check for matches in the sender, subject, or body
        if (pd.notna(row['Keywords']) and (row['Keywords'].lower() in email_sender.lower() or
                                           row['Keywords'].lower() in email_subject.lower() or
                                           row['Keywords'].lower() in email_body.lower())) or \
                (pd.notna(row['Sender']) and row['Sender'].lower() in email_sender.lower()) or \
                (pd.notna(row['Subject']) and row['Subject'].lower() in email_subject.lower()):
            return False  # Skip classification if a match is found

    # Preprocess the sender's email if necessary (e.g., extracting the domain)
    sender_domain = email_sender.split('@')[-1]

    # Combine sender, subject, and body as input to the model
    email_content = f"{sender_domain} {email_subject} {email_body}"

    # Predict using the model
    prediction = model.predict([email_content])

    # Assuming the model is trained such that '1' indicates spam
    return prediction[0] == 1


def move_email_to_spam(mail: imaplib.IMAP4_SSL, email_id: str, log_func: Callable[[str], None]) -> None:
    """
    Moves an email to the 'Spam' folder. Uses the copy and delete approach if the MOVE command is not supported.
    """
    try:
        spam_folder_name = 'Spam'
        # Attempt to use the MOVE command if available
        try:
            mail.uid('MOVE', email_id, spam_folder_name)  # Using UID to ensure the correct email is targeted
            log_func("Email successfully moved to Spam using MOVE.")
        except AttributeError:
            # Fallback to COPY then DELETE if MOVE is not available
            mail.uid('COPY', email_id, spam_folder_name)
            mail.uid('STORE', email_id, '+FLAGS', '(\\Deleted)')
            mail.expunge()
            log_func("Email successfully moved to Spam using COPY and DELETE.")
    except imaplib.IMAP4.error as e:
        log_func(f"Error moving email to Spam: {e}.")
    print_separator(log_func)


def load_json_file(file_path: Path, log_func: Callable[[str], None]) -> Optional[Dict]:
    """
    Loads and returns the content of a JSON file.
    """
    try:
        with file_path.open('r') as file:
            log_func("Loading email configuration...")
            return json.load(file)
    except FileNotFoundError:
        log_func(f"{file_path} not found.")
        return None
    except json.JSONDecodeError:
        log_func(f"Error decoding JSON from {file_path}.")
        return None


def get_and_filter_emails(mail: imaplib.IMAP4_SSL, usr: str, pw: str, keep_df: pd.DataFrame, model,
                          log_func: Callable[[str], None],
                          add_to_list_func: Callable[[str, str, str, str], None]) -> None:
    """
    Connects to an email account, identifies spam emails, and moves them to a 'Spam' folder.
    """
    print_separator(log_func)
    log_func("Connecting to email server...")
    mail.login(usr, pw)
    mail.select('inbox')
    log_func("Connection successful. Fetching emails...")

    result, data = mail.search(None, "All")
    email_ids = data[0].split()[:100]

    create_spam_folder(mail, log_func)

    for email_id in email_ids:
        result, data = mail.fetch(email_id, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = msg['subject']
        from_ = msg['from']
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        if is_spam(from_, subject, body, model, keep_df):
            log_func(f"***SPAM DETECTED***: From: {from_}, Subject: {subject[:30]}...")
            add_to_list_func(email_id.decode(), from_, subject, body)

    print_separator(log_func)
    log_func("Email filtering complete.")


if __name__ == "__main__":
    print("------------------------------------------------")
    print("Starting email filter process...")
    model_path = '../models/spam_classifier.joblib'
    model = load_model(model_path, None)  # This will now correctly reference the defined load_model function

    email_info = load_json_file(Path("../data/email_data.json"), None)
    if email_info:
        user = email_info.get("gmail_personal", {}).get("user")
        password = email_info.get("gmail_personal", {}).get("pass")
        if user and password:
            print("Email credentials loaded successfully.")
            if model is not None:
                get_and_filter_emails(user, password, model, None)  # Make sure to pass the model as an argument
            else:
                print("Failed to load or create the machine learning model.")
        else:
            print("Email credentials are missing in the loaded JSON.")
    else:
        print("Failed to load email credentials.")
    print("Process completed.")
    print("------------------------------------------------")
