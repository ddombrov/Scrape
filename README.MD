# Google Scholar Bibliometrics Web Scraper

## Summary

This project is designed to scrape Google Scholar Bibliometrics data using Python, allowing you to collect information such as the h-index, citations, and other scholarly metrics.

## Understanding the Files

1. **urls.txt**:  
   This file should contain all the URLs you want to scrape. Try to run 20 URLs at one time (more URLs may time out and the program will just end abruptly with no warning)

2. **year.txt**:  
   Specify the year you want to scrape. For example, entering "2023" will scrape data for the period from May 2023 to April 2024.

3. **output.csv**:  
   After scraping, upload this file to Excel or Google Sheets for further analysis.

4. **log.txt**:  
   This file logs any issues requiring manual inspection. If a profile needs review, you'll need to handle the entire profile unless it exceeds 20 articles; in that case, the first 20 articles will be processed for you. For individual articles flagged in the log, you’ll need to complete the review manually. Otherwise, the scraping is considered complete.

5. **google_scholar_web_scraping.py**:  
   This script contains all the code required to run the scraper.

6. **keywords.py**:  
   This file is where you can add, remove, or change certain keywords to detect article types.

## Using the Scraper Online

1. **Create Accounts**:  
   Sign up for accounts on Replit (skip the tutorial). If it asks you for information, enter CEPS Testing for the name, Beginner level for experience, Python for the language, and Personal Use for the purpose.

2. **Import from GitHub**:  
   Click the "Import from GitHub" option (right below the "Create Repl" button).

3. **Import from URL**:  
   In the popup, under "Import from GitHub," paste the following URL under "From URL":
   https://github.com/ddombrov/Scrape.git and then click the button "Import from GitHub" at the bottom.

4. **Change the Starting Files**:  
   Click the plus button to create a new tab. From the options, select "File" (find a file), then select the file you need to change. Do this for `urls.txt` and `year.txt`.

5. **Install the Required Dependencies**:  
   Click the "Run" button at the top of the Replit interface to start the script.

6. **Run the Script**:  
   Open the Shell tab and run the following command:

```bash
python google_scholar_web_scraping.py > log.txt 2>&1
```

### Using the Scraper Locally

1. **Prerequisites**
   Before you start, make sure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/). This project was created with Python version 3.11.
   Ensure that you are able to activate Python environments (see Troubleshooting for help if issues occur).

2. **Open your terminal**
   Mac/Linux:
   Open the terminal
   Windows:
   Open the Command Prompt

3. **Clone the repository**:
   Run the following commands by pasting them into the terminal:

```bash
   git clone https://github.com/ddombrov/Scrape.git
   cd Scrape
```

4. **Set up the virtual environment and install dependencies:**:
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

5. **Running the script**:
   Run the following commands by pasting them into the terminal:

```bash
   python google_scholar_web_scraping.py
```

## Troubleshooting

1. **Support (Local or Online):**

For any unresolved issues, please contact me, Daniel Dombrovsky, at ddombrov@uoguelph.ca.

2. **Scraping Google Error Codes (Local or Online):**

You may get an error informing you of too many scrapes ex. Error fetching final URL: 429 Client Error.

2.1. **Reduce the amount of URLs:**
Google may be restricting your access and you may need to process only 10 URLs at a time.

2.2. **Reduce Request Frequency:**
Increase the sleep time between each URL request to avoid hitting rate limits.

2.3. **Use a Different IP Address or Proxy:**
If possible, switch to a different IP address or proxy to see if the issue persists. This would be easiest by switching to a new Replit file or switching from local/online to the other.

3. **Python Enviornment Activation (Local):**

How to reactive python enviornment.

3.1. **Delete the current enviornment:**
Try deleting the current enviornment:

        Windows:

```bash
rmdir venv
```

    Mac:

```bash
rm -rf venv
```

3.2. **Reinstall the Dependencies:**
Reinstall the dependencies and setup the virtual enviornment:

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

4. **Invalid Permissions (Local):**

This explains the steps to change the execution policy:

4.1. **Open PowerShell as Administrator:**
Right-click the Start menu and select "Windows PowerShell (Admin)" or "Windows Terminal (Admin)" if you're using Windows 10 or 11.

4.2. **Check the Current Execution Policy:**
Run the following command to see your current execution policy:

```bash
Get-ExecutionPolicy
```

4.3. **Change Current Execution Policy:**
If the execution policy is too restrictive (e.g., Restricted), you can change it to RemoteSigned, which allows scripts that you create locally to run, but requires that scripts downloaded from the internet be signed by a trusted publisher.

```bash
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

4.4. **Confirm the Change:**
Type Y when prompted.

4.5. **Try Activating the Virtual Environment Again:**
Once the execution policy is changed, you should be able to activate your virtual environment with:

        Windows:

```bash
    venv\Scripts\Activate
```

    Mac:

```bash
source venv/bin/activate
```

4.6. **Reverting the Execution Policy (Optional):**
If you want to revert the execution policy to its original state after activating the environment, you can do so by running: Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser

## To Do

1. **Incorporate Clicking:**
   Add Selenium/AJAX functionality to be able to click "Read more" and handle more than 20 articles.
2. **Trim the Name:**
   Remove PhD, random characters from names (may not be possible to determine what is middle name and not title)
3. **Update URLS automatically:**
   For example, Gary's was https://scholar.google.com/citations?user=O2yw-uoAAAAJ&hl=en and is now https://scholar.google.com/citations?user=wl3BrEUAAAAJ&hl=en (program cannot handle this)
4. **Remove Year Period Total**
   Only need total for "Citations"
