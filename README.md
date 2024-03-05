# EmailSpamDetectorApp

A Python-based email spam detection tool utilizing machine learning for real-time filtering. It features customizable criteria, adaptive learning, and supports dark/light themes.

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

## Contributing
Contributions to EmailSpamDetectorApp are welcome! Please open an issue or submit a pull request with your proposed changes or improvements.

## License
Distributed under the MIT License. See `LICENSE` for more information.
