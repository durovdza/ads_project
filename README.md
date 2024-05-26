# ads_project
Applied Data Science Project FS24

## Team Members

- Anna Wiedmer
- Dzana Durovic
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

#Before you run the python script data_collection_web_scraping.py, you need to change the driver path which is already given in the script with your own driver path
![image](https://github.com/durovdza/ads_project/assets/65607306/fc2212b1-b234-4589-85b4-8abe0b2cf104)


# Run the local development server or script (specify the script if it's not 'app.py')
python app.py


