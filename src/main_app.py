import imaplib
import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext, Listbox

import customtkinter as ctk
import pandas as pd
from PIL import Image

from src.spam_detector import load_model, load_json_file, get_and_filter_emails, move_email_to_spam

ctk.set_appearance_mode("Dark")  # Default theme
ctk.set_default_color_theme("dark-blue")


class EmailDetailsDialog(ctk.CTkToplevel):
    def __init__(self, parent, email_details):
        super().__init__(parent)
        self.title("Email Details")
        self.geometry("400x300")

        # Make the dialog modal
        self.transient(parent)
        self.grab_set()

        # Sender
        sender_label = ctk.CTkLabel(self, text="Sender:", anchor="w")
        sender_label.pack(fill="x", padx=20, pady=(10, 0))
        sender_value = ctk.CTkLabel(self, text=email_details["from"], anchor="w")
        sender_value.pack(fill="x", padx=20, pady=(0, 10))

        # Subject
        subject_label = ctk.CTkLabel(self, text="Subject:", anchor="w")
        subject_label.pack(fill="x", padx=20, pady=(10, 0))
        subject_value = ctk.CTkLabel(self, text=email_details["subject"], anchor="w")
        subject_value.pack(fill="x", padx=20, pady=(0, 10))

        # Body in a scrollable frame
        body_label = ctk.CTkLabel(self, text="Body:", anchor="w")
        body_label.pack(fill="x", padx=20, pady=(10, 0))
        body_scroll = ctk.CTkScrollbar(self)
        body_text = tk.Text(self, yscrollcommand=body_scroll.set, wrap="word")
        body_scroll.configure(command=body_text.yview)
        body_scroll.pack(side="right", fill="y", pady=(0, 10))
        body_text.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        body_text.insert("1.0", email_details["body"])
        body_text.configure(state="disabled")  # Make the text widget read-only


class CustomCredentialDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Credential Name")
        self.geometry("300x150")
        self.parent = parent

        # Make the dialog modal
        self.transient(parent)
        self.grab_set()

        self.credential_name = None

        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)  # Handle window close button

    def setup_ui(self):
        self.label = ctk.CTkLabel(self, text="Enter a name for this credential:", anchor="w")
        self.label.pack(pady=(20, 10), padx=20, fill="x")

        self.entry = ctk.CTkEntry(self)
        self.entry.pack(pady=(0, 20), padx=20, fill="x")
        self.entry.focus_set()

        self.save_button = ctk.CTkButton(self, text="Save", command=self.on_save)
        self.save_button.pack(side="right", padx=20, pady=10)

        self.cancel_button = ctk.CTkButton(self, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side="right", pady=10)

    def on_save(self):
        self.credential_name = self.entry.get()
        if not self.credential_name:
            ctk.CTkMessageBox.show_info("Information", "Please enter a credential name.")
            return
        self.close_dialog()

    def on_cancel(self):
        self.credential_name = None  # Ensure name is None if cancelled
        self.close_dialog()

    def close_dialog(self):
        self.grab_release()  # Release the grab to make the parent window accessible again
        self.destroy()

    def show(self):
        self.wait_window(self)  # Wait here until the dialog is closed
        return self.credential_name


class SpamDetectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.email_details = {}  # Initialize a dictionary to store email details
        self.mail = None  # Initialize the mail server

        self.title('Email Spam Detector')
        self.geometry('1300x700')

        self.credentials_file = Path("../data/email_data.json")
        self.credentials = self.load_credentials()

        # Main layout frames
        self.setup_layout_frames()

        # Input section
        self.setup_input_section()

        # Output sections
        self.setup_output_sections()

        # Theme selection section
        self.setup_theme_selection()

    def setup_layout_frames(self):
        self.left_frame = ctk.CTkFrame(self, corner_radius=10)
        self.left_frame.pack(side='left', fill='both', expand=True, padx=(20, 10), pady=20)

        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.pack(side='left', fill='both', expand=True, padx=(10, 20), pady=20)

        self.bottom_frame = ctk.CTkFrame(self, corner_radius=10)
        self.bottom_frame.pack(side='bottom', fill='x', padx=20, pady=(10, 20))

    def setup_input_section(self):
        # Credentials selection dropdown and label
        self.credentials_dropdown_label = ctk.CTkLabel(self.left_frame, text="Select Saved Credentials:",
                                                       font=("Arial", 10))
        self.credentials_dropdown_label.pack(pady=(10, 5))
        self.credentials_dropdown = ctk.CTkComboBox(self.left_frame, width=300, command=self.on_credentials_select)
        self.credentials_dropdown.pack(side="top", pady=5, padx=(0, 10), fill='x')

        # User Credentials section title
        self.user_pass_section_title = ctk.CTkLabel(self.left_frame, text="User Credentials",
                                                    font=("Arial", 12, "bold"))
        self.user_pass_section_title.pack(pady=(10, 0))

        # Error label for displaying messages, placed above the email entry
        self.error_label = ctk.CTkLabel(self.left_frame, text="", font=("Arial", 10), text_color="red")
        self.error_label.pack(pady=(5, 0))

        # Email entry and label
        self.email_label = ctk.CTkLabel(self.left_frame, text="Email:", font=("Arial", 10))
        self.email_label.pack(pady=(5, 2))
        self.email_entry = ctk.CTkEntry(self.left_frame, width=400, placeholder_text="Enter your email")
        self.email_entry.pack(pady=(0, 10))

        # Password entry and label
        self.password_label = ctk.CTkLabel(self.left_frame, text="Password:", font=("Arial", 10))
        self.password_label.pack(pady=(10, 2))
        self.password_entry = ctk.CTkEntry(self.left_frame, show="*", width=400,
                                           placeholder_text="App-specific password")
        self.password_entry.pack(pady=(0, 10))

        # Save credentials button, placed below the password entry
        self.save_credentials_button = ctk.CTkButton(self.left_frame, text="Save Credentials",
                                                     command=self.save_credentials)
        self.save_credentials_button.pack(pady=(5, 20))

        # Number of emails entry and label
        self.num_emails_label = ctk.CTkLabel(self.left_frame, text="Number of Emails to Check:", font=("Arial", 10))
        self.num_emails_label.pack(pady=(10, 2))
        self.num_emails_entry = ctk.CTkEntry(self.left_frame, width=400, placeholder_text="Number of emails to check")
        self.num_emails_entry.pack(pady=(0, 20))

        # Run detection button
        self.run_button = ctk.CTkButton(self.left_frame, text="Detect Spam Emails", command=self.run_spam_detection)
        self.run_button.pack(pady=(10, 0), fill='x')

        # Populate the dropdown with saved credentials
        self.populate_credentials_dropdown()

    def setup_output_sections(self):
        self.command_output_title = ctk.CTkLabel(self.right_frame, text="Command Output", font=("Arial", 12, "bold"))
        self.command_output_title.pack(pady=(0, 5))

        self.console_output = scrolledtext.ScrolledText(self.right_frame, bg="#2e2e2e", fg="white", font=("Arial", 10))
        self.console_output.pack(padx=10, pady=(0, 10), fill='both', expand=True)

        self.spam_list_title = ctk.CTkLabel(self.right_frame, text="Spam Emails Detected", font=("Arial", 12, "bold"))
        self.spam_list_title.pack(pady=(5, 5))

        self.spam_listbox = Listbox(self.right_frame, bg="#2e2e2e", fg="white", height=10, font=("Arial", 10),
                                    borderwidth=0, highlightthickness=0,
                                    selectmode='multiple')  # selectmode='multiple' allows multiple selection
        self.spam_listbox.pack(padx=10, pady=(0, 10), fill='both', expand=True)
        self.spam_listbox.bind("<Double-1>", lambda event: self.view_email_details())

        self.select_all_button = ctk.CTkButton(self.right_frame, text="Select All", command=self.select_all)
        self.select_all_button.pack(side="left", padx=(0, 5), pady=(10, 0))

        self.remove_spam_button = ctk.CTkButton(self.right_frame, text="Remove Spam!!!",
                                                command=self.remove_selected_spam_threaded, fg_color="#FF5733",
                                                text_color="white")
        self.remove_spam_button.pack(side="right", padx=(5, 0), pady=(10, 0))

        # Add an icon to the button
        img = Image.open("../assets/devil-icon.png")
        self.remove_spam_button.icon = ctk.CTkImage(img)
        self.remove_spam_button.configure(image=self.remove_spam_button.icon, compound="left")

    def setup_theme_selection(self):
        self.theme_label = ctk.CTkLabel(self.bottom_frame, text="Theme Selection", font=("Arial", 12, "bold"))
        self.theme_label.pack(pady=(0, 5))

        self.theme_combobox = ctk.CTkComboBox(self.bottom_frame, values=["Dark", "Light"], command=self.change_theme)
        self.theme_combobox.set("Dark")  # Default value
        self.theme_combobox.pack(pady=10)

    def run_spam_detection(self):
        threading.Thread(target=self.process_emails, args=()).start()

    def load_credentials(self):
        if self.credentials_file.exists():
            with open(self.credentials_file, 'r') as file:
                return json.load(file)
        return {}

    def populate_credentials_dropdown(self):
        if self.credentials:
            # Extract the list of keys (credential names) from the credentials dict
            credential_names = list(self.credentials.keys())

            # Update the CTkComboBox's values with the list of credential names
            self.credentials_dropdown.configure(values=credential_names)

            # Automatically select the first set of credentials to fill in the fields
            first_key = credential_names[0]
            self.credentials_dropdown.set(first_key)
            self.on_credentials_select(first_key)
        else:
            # If there are no credentials, clear the combobox and input fields
            self.credentials_dropdown.configure(values=[])
            self.email_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)

    def on_credentials_select(self, selection):
        # Update the input fields based on the selected credential set
        if selection in self.credentials:
            credentials = self.credentials[selection]
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, credentials.get('user', ''))
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, credentials.get('pass', ''))

    def save_credentials(self):
        user = self.email_entry.get()
        password = self.password_entry.get()
        if not user or not password:
            ctk.CTkMessageBox.show_info("Information", "Please enter both user and password")
            return

        dialog = CustomCredentialDialog(self)
        name = dialog.show()

        if not name:
            return

        self.credentials[name] = {"user": user, "pass": password}
        with open(self.credentials_file, 'w') as file:
            json.dump(self.credentials, file, indent=4)

        self.populate_credentials_dropdown()
        self.credentials_dropdown.set(name)

    def change_theme(self, theme):
        ctk.set_appearance_mode(theme.lower())

    def log_to_console(self, message):
        self.console_output.insert(tk.END, message + "\n")
        self.console_output.see(tk.END)

    def process_emails(self):
        self.log_to_console("------------------------------------------------")
        self.log_to_console("Starting email filter process...")
        model_path = '../models/spam_classifier.joblib'
        model = load_model(model_path, self.log_to_console)  # Ensure load_model accepts a logging function

        # Try to get user and password from GUI inputs
        gui_user = self.email_entry.get().strip()
        gui_password = self.password_entry.get().strip()

        email_info = load_json_file(Path("../data/email_data.json"),
                                    self.log_to_console)  # Ensure load_json_file accepts a logging function

        user, password = None, None

        if gui_user and gui_password:
            self.log_to_console("Using credentials from the application.")
            user, password = gui_user, gui_password
        elif email_info:
            if gui_user:
                # Look for the user in the JSON file
                for account_type, credentials in email_info.items():
                    if credentials.get("user") == gui_user:
                        self.log_to_console(f"Matching user found in JSON for '{account_type}'.")
                        user = credentials.get("user")
                        password = credentials.get("pass")
                        break
            if not user or not password:
                # Fallback to first account in JSON if no specific user is given or found
                first_key = next(iter(email_info))
                self.log_to_console(
                    f"No specific user found. Falling back to the first account in JSON: '{first_key}'.")
                user = email_info[first_key].get("user")
                password = email_info[first_key].get("pass")

        if user and password:
            self.log_to_console("Email credentials loaded successfully.")
            # Determine mail server from username
            if not self.determine_mail_server(user):
                return

            # Check for keep_data.csv and update it with the table data
            keep_data_path = Path("../data/keep_data.csv")
            if keep_data_path.exists():
                keep_data_df = pd.read_csv(keep_data_path)
            else:
                keep_data_df = pd.DataFrame(columns=["Keywords", "Sender", "Subject"])

            # Remove duplicates
            keep_data_df.drop_duplicates(inplace=True)

            if model is not None:
                get_and_filter_emails(self.mail, user, password, keep_data_df, model,
                                      self.log_to_console, self.add_email_to_list)
            else:
                self.log_to_console("Failed to load or create the machine learning model.")
        else:
            self.log_to_console("Email credentials are missing or incomplete.")

        self.log_to_console("Process completed.")
        self.log_to_console("------------------------------------------------")

    def determine_mail_server(self, username):
        # Try to determine the mail server from the username
        # This is just a basic example, you may need to refine it for your use case
        mail_servers = {
            "gmail.com": "imap.gmail.com",
            "outlook.com": "outlook.office365.com",
            "yahoo.com": "imap.mail.yahoo.com",
            "aol.com": "imap.aol.com",
            "icloud.com": "imap.mail.me.com",
            "zoho.com": "imap.zoho.com",
            "protonmail.com": "imap.protonmail.ch",
            "mail.com": "imap.mail.com",
            "yandex.com": "imap.yandex.com",
            "gmx.com": "imap.gmx.com",
            "hotmail.com": "imap-mail.outlook.com",
            "live.com": "imap-mail.outlook.com",
            "msn.com": "imap-mail.outlook.com",
            "me.com": "imap.mail.me.com",
            "att.net": "imap.mail.att.net",
            "verizon.net": "incoming.verizon.net",
            "cox.net": "imap.cox.net",
            "charter.net": "mobile.charter.net",
            "earthlink.net": "imap.earthlink.net",
            "rr.com": "mail.twc.com",
            # Add more mail server mappings as needed
        }
        domain = username.split('@')[-1]  # Get domain from username
        self.mail = imaplib.IMAP4_SSL(mail_servers.get(domain))  # Get mail server based on domain
        if not self.mail:
            # If mail server cannot be determined, display error message
            self.email_entry.configure(text_color="red")  # Set border color to red to indicate error
            self.error_label.configure(
                text=f"Mail server for '{domain}' not supported. Please include the full email address.")
            return False
            # Adjust the appearance of the email entry widget to indicate the error
        else:
            self.email_entry.configure(text_color="white")  # Reset border color if mail server is determined
            self.error_label.configure(text="")  # Clear error message
            return True


    def remove_selected_spam_threaded(self):
        threading.Thread(target=self.remove_selected_spam, args=()).start()

    def remove_selected_spam(self):
        selected_indices = self.spam_listbox.curselection()  # Get indices of selected items

        if not selected_indices:
            self.log_to_console("No emails selected.")
            return

        for index in selected_indices:
            # Retrieve the detailed email information using the listbox index
            email_detail = self.email_details.get(index)
            if email_detail:
                email_id = email_detail["email_id"]
                move_email_to_spam(self.mail, email_id, self.log_to_console)
                self.log_to_console(f"Moved to Spam: {email_detail['from']}: {email_detail['subject']}")

        # Clear the listbox and dictionary of processed emails
        for i in reversed(selected_indices):
            self.spam_listbox.delete(i)
            # Also remove from the email_details dictionary if necessary
            if i in self.email_details:
                del self.email_details[i]

        self.log_to_console("Selected spam emails have been moved.")

    def add_email_to_list(self, email_id, from_, subject, body):
        listbox_index = self.spam_listbox.size()
        self.spam_listbox.insert(tk.END, f"{from_}: {subject}")
        # Store the email details associated with this listbox entry
        self.email_details[listbox_index] = {"email_id": email_id, "from": from_, "subject": subject, "body": body}

    def view_email_details(self):
        selected_indices = self.spam_listbox.curselection()
        if not selected_indices:
            return  # No selection made
        selected_index = selected_indices[0]  # Assuming single selection
        email_details = self.email_details.get(selected_index)
        if email_details:
            EmailDetailsDialog(self, email_details)

    def select_all(self):
        self.spam_listbox.select_set(0, tk.END)


if __name__ == "__main__":
    app = SpamDetectorApp()
    app.mainloop()
