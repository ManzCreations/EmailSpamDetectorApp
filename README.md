# EmailSpamDetectorApp

A sophisticated email spam detection application that leverages machine learning to filter out unwanted emails. Built with Python, it integrates seamlessly with email servers to process incoming messages in real-time. Features include customizable spam filtering criteria, a user-friendly interface with dark and light themes, and the ability to learn and adapt to new spam patterns over time.

## Features

- **Machine Learning Integration**: Leverages a pre-trained model to classify emails as spam or not spam.
- **Customizable Filtering Criteria**: Users can specify keywords or senders to bypass spam filtering.
- **Theme Support**: Offers both dark and light themes for user preference.
- **Real-Time Processing**: Filters emails as they arrive, integrating seamlessly with email servers.

## Installation

To install EmailSpamDetectorApp, clone this repository and install the required dependencies:

```
git clone https://github.com/ManzCreations/EmailSpamDetectorApp.git
cd EmailSpamDetectorApp
pip install -r requirements.txt
```

## Acquiring a Third-Party Email Password
To use EmailSpamDetectorApp, you'll need to generate a third-party app password for your email account. For Gmail users:
1. Visit [Google's App Passwords Page](https://www.getmailbird.com/gmail-app-password/). This process can be assumed for any email server.
2. Follow the instructions to generate an app password.
3. Use this password as your password to use for the application.
   

## Using EmailSpamDetectorApp

To start the application, run:
```
cd src
python main_app.py
```
Follow the on-screen instructions to configure your email server and specify any filtering criteria.

## Workflow
1. **Launch the Application**: Launch the app and choose your theme.
![image](https://github.com/ManzCreations/EmailSpamDetectorApp/assets/128404387/524ba4c5-be52-40d6-9cd6-f2788c7d524a)
2. **Enter Email Credentials**: Use your full email as the username and the third-party app password as the password. Click "Save Credentials" to store them for later use.
![image](https://github.com/ManzCreations/EmailSpamDetectorApp/assets/128404387/c9738af1-04c7-45a2-965e-ab4dee9e871f)
3. **Detect Spam Emails**: Click "Detect Spam Emails" to analyze your inbox and generate a list of potential spam.
![image](https://github.com/ManzCreations/EmailSpamDetectorApp/assets/128404387/b48a01a1-8de7-4833-834f-3fbe8e68838e)
4. **Review and Remove Spam**: In the list at the bottom right, double-click any email to see more details. Select emails and click "Remove Spam" to delete them from your inbox.
![image](https://github.com/ManzCreations/EmailSpamDetectorApp/assets/128404387/caf95fbf-3b8c-4bd8-885c-c0847f54f5b8)
5. **All Done!!**: Come back tomorrow and the next day to do it again and remove your pesky spam problem.
![image](https://github.com/ManzCreations/EmailSpamDetectorApp/assets/128404387/522580fb-4eeb-4b8a-92d9-bfc98cc3ea31)

## Customizing Spam Detection Criteria

To refine spam detection and ensure certain emails are kept, you can create a `keep_data.csv` file in the `data` folder. This CSV file can include keywords, sender addresses, or subjects that you wish to exclude from spam detection. Here's how:

1. **Create `keep_data.csv`**: Navigate to the `data` folder in your EmailSpamDetectorApp directory. Create a new CSV file named `keep_data.csv`.

2. **Add Custom Criteria**: Open `keep_data.csv` in a text editor or spreadsheet software. Add your criteria in the following format:

    ```
    Keywords,Sender,Subject
    keyword1,example@domain.com,subject1
    keyword2,,subject2
    ,,subject3
    ```

    - **Keywords**: Any word or phrase you wish to filter out from spam detection.
    - **Sender**: Specific email addresses that should not be flagged as spam.
    - **Subject**: Subjects that, when matched, prevent emails from being marked as spam.

3. **Save Changes**: After adding your custom criteria, save `keep_data.csv`.

The EmailSpamDetectorApp will automatically read `keep_data.csv` and apply these criteria during spam detection, ensuring emails that match your specifications are kept.

![image](https://github.com/ManzCreations/EmailSpamDetectorApp/assets/128404387/bfa27ff1-21db-41b2-ae6e-9b41abd8d01d)

This feature allows you to personalize the spam detection process, ensuring important emails remain in your inbox.

## Contributing
Contributions to EmailSpamDetectorApp are welcome! Please open an issue or submit a pull request with your proposed changes or improvements.

## License
Distributed under the MIT License. See `LICENSE` for more information.
