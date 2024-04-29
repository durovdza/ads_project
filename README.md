# ads_project
Applied Data Science Project FS24

## Team Members

- Anna Wiedmer
- Dzana Ducovic
- Sophie Maier

## Overview

Insert description of project


### Prerequisites

Following must be installed on your system:

- Python
- Git
- MySQL 

### Setup

Here's how you can set up your development environment:

```bash
# Clone the repository
git clone https://github.com/durovdza/ads_project

# Create a API key from chat gpt on their website and replace "YOUR KEY" with your key. After that, create a '.env' file in the 'OpenDataHack2023' directory with the following content
echo OPENAI_API_KEY="YOUR KEY" >> .env

# Insert your Database Credentials in the file "mysql_credentials.txt"
In order to get these information, you have to connect to your database in MySQL Workbench and go to Database / Manage Connections...

# Navigate to the project directory
cd ads_project

# Create a Python virtual environment in the 'venv' directory
py -m venv venv

# Activate the virtual environment (use the correct command for your operating system)
venv\Scripts\activate # For Windows in Git Bash
# or
source venv/bin/activate # For Unix or Linux systems

# Install the project dependencies from 'requirements.txt'
pip install -r requirements.txt

# Run the local development server or script (specify the script if it's not 'app.py')
flask run
