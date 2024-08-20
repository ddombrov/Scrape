# Google Scholar Web Scraping

This project is designed to scrape Google Scholar using Python. The script fetches data such as h-index, citations, and other scholarly metrics.

## Getting Started
1. run 'npm install'
2. run 'npm start'

### Prerequisites

Before you start, make sure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/). This was created with Python version 3.11. 

### Installation

1. **Open your terminal** (Command Prompt on Windows, Terminal on Mac/Linux).

2. **Clone the repository**:

   Run each of the following lines (either all together or one by one)

      git clone https://github.com/ddombrov/Scrape.git
      cd Scrape
      python -m venv venv
      source .venv/bin/activate (on Mac) or .venv\Scripts\activate (on Windows) 

   How to enable activation if you run into an issue (Steps to Change the Execution Policy): 
      1. Open PowerShell as Administrator:
      2. Right-click the Start menu and select "Windows PowerShell (Admin)" or "Windows Terminal (Admin)" if you're using Windows 10 or 11.
      3. Check the Current Execution Policy:4
      4. Run the following command to see your current execution policy:
      Get-ExecutionPolicy
      5. If the execution policy is too restrictive (e.g., Restricted), you can change it to RemoteSigned, which allows scripts that you create locally to run, but requires that scripts downloaded from the internet be signed by a trusted publisher.
      Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
      6. Confirm the change by typing Y when prompted.
      7. Try Activating the Virtual Environment Again:
      8. Once the execution policy is changed, you should be able to activate your virtual environment with:
      .\.venv\Scripts\Activate

   Reverting the Execution Policy (Optional):
   1. If you want to revert the execution policy to its original state after activating the environment, you can do so by running:
   Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser


