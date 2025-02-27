# 🤖 Automation Updater Bot

Welcome to the **Automation Updater Bot** repository! This project is designed to streamline the process of updating applications on Linux systems by automating tasks such as downloading updates, creating changelogs, and sending notifications. By integrating these functionalities, the bot ensures that your applications remain current with minimal manual intervention.

## 📋 Project Overview

The primary objectives of this project include:

- **Automated Application Updates**: Seamlessly download and install the latest versions of applications.
- **Changelog Generation**: Automatically generate detailed changelogs to keep track of updates and modifications.
- **Email Notifications**: Notify users or administrators about updates and changes via email.

## 🛠️ Features

- **Application Update Automation**: 
  - *applinux.py*: Manages the download and installation of application updates on Linux systems.
- **Changelog Creation**: 
  - *changelog_creater.py*: Generates comprehensive changelogs detailing the updates and changes made.
- **Email Notification System**: 
  - *mailer.py*: Sends out email notifications to inform stakeholders about the latest updates and changes.

## 🧰 Tech Stack

- **Programming Language**: ![Python](https://img.shields.io/badge/Python-3.8-blue)
- **Libraries**:
  - `smtplib`: For sending emails.
  - `os`: For interacting with the operating system.
  - `subprocess`: For executing system commands.
  - `datetime`: For handling date and time operations.

## 🚀 Getting Started

Follow these steps to set up the project locally:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ashenbandara02/automation-updater-bot.git
   cd automation-updater-bot
