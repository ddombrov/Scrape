# Google Scholar Web Scraping

This project is designed to scrape Google Scholar using Python. The script fetches data such as h-index, citations, and other scholarly metrics.

### Using the Scrape Online

1. Create Accounts: Sign up for accounts on Replit and GitHub.
2. Clone the Repository: Copy the GitHub repository URL.
3. Import to Replit:
   Go to Replit and import the repository using the copied URL.
   Replit will handle the setup for you.
4. Run the Script:
   Click the Run button at the top of the Replit interface to start the script.
5. Open the Shell tab and run the following command:

```bash
python google_scholar_web_scraping.py
```

### Using the Scraper Locally

0. **Prerequisites**

   Before you start, make sure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/). This project was created with Python version 3.11.

   Ensure that you are able to activate Python environments (see Troubleshooting for help if issues occur).

1. **Open your terminal**

   Mac/Linux:
   Open the terminal

   Windows:
   Open the Command Prompt

2. **Clone the repository**:

   Run the following commands by pasting them into the terminal:

```bash
   git clone https://github.com/ddombrov/Scrape.git
   cd Scrape
```

3. **Set up the virtual environment and install dependencies:**:

   Run the following commands by pasting them into the terminal:

   Mac:

```bash
   python -m venv venv
   source venv/bin/activate
   pip install beautifulsoup4
   pip install requests
```

Windows:

```bash
   python -m venv venv
   venv\Scripts\activate
   pip install beautifulsoup4
   pip install requests
```

4. **Running the script**:
   Run the following commands by pasting them into the terminal:

```bash
   python google_scholar_web_scraping.py
```

### Troubleshooting

**A: How to enable activation if you run into an issue (Steps to Change the Execution Policy):**

1.  Open PowerShell as Administrator. Right-click the Start menu and select "Windows PowerShell (Admin)" or "Windows Terminal (Admin)" if you're using Windows 10 or 11.

2.  Check the Current Execution Policy. Run the following command to see your current execution policy:

```bash
    Get-ExecutionPolicy
```

3.  If the execution policy is too restrictive (e.g., Restricted), you can change it to RemoteSigned, which allows scripts that you create locally to run, but requires that scripts downloaded from the internet be signed by a trusted publisher.

```bash
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

4.  Confirm the change by typing Y when prompted.

5.  Try Activating the Virtual Environment Again: Once the execution policy is changed, you should be able to activate your virtual environment with:

    Windows:

```bash
    venv\Scripts\Activate
```

    Mac:

```bash
source venv/bin/activate
```

6.  Reverting the Execution Policy (Optional): If you want to revert the execution policy to its original state after activating the environment, you can do so by running: Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser

**B: How to reactive python enviornment:**

1.  Try deleting the current enviornment:

    Windows:

```bash
rmdir venv
```

    Mac:

```bash
rm -rf venv
```

2.  Reinstall the dependencies and setup the virtual enviornment:

    Mac:

```bash
    python -m venv venv
    source venv/bin/activate
    pip install beautifulsoup4
    pip install requests
```

    Windows:

```bash
    python -m venv venv
    venv\Scripts\activate
    pip install beautifulsoup4
    pip install requests
```
