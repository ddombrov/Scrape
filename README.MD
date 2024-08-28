# Google Scholar Web Scraping

## Summary

This project is designed to scrape Google Scholar using Python, allowing you to collect data such as the h-index, citations, and other scholarly metrics.

## Support

For any unresolved issues, please contact me, Daniel Dombrovsky, at ddombrov@uoguelph.ca.

## Understanding the Files

1. **urls.txt**:  
   This file should contain all the URLs you want to scrape.

2. **year.txt**:  
   Specify the year you want to scrape. For example, entering "2023" will scrape data for the period from May 2023 to April 2024.

3. **output.csv**:  
   After scraping, upload this file to Excel or Google Sheets for further analysis.

4. **log.txt**:  
   This file logs any issues requiring manual inspection. If a profile needs review, you'll need to handle the entire profile unless it exceeds 20 articles; in that case, the first 20 articles will be processed for you. For individual articles flagged in the log, you’ll need to complete the review manually. Otherwise, the scraping is considered complete.

5. **summary.csv**:  
   After scraping, this file does the total and average math.

6. **google_scholar_web_scraping.py**:  
   This script contains all the code required to run the scraper.

7. **keywords.py**:  
   This file is where you can add, remove, or change certain keywords to detect article types.

## Using the Scraper Online

1. **Create Accounts**:  
   Sign up for accounts on Replit (skip the tutorial).

2. **Import from GitHub**:  
   Click the "Import from GitHub" option (right below the "Create Repl" button).

3. **Import from URL**:  
   In the popup, under "Import from GitHub," paste the following URL under "From URL":
   https://github.com/ddombrov/Scrape.git

4. **Change the Starting Files**:  
   Click the plus button to create a new tab. From the options, select "File" (find a file), then select the file you need to change. Do this for `urls.txt` and `year.txt`.

5. **Install the Required Dependencies**:  
   Click the "Run" button at the top of the Replit interface to start the script.

6. **Run the Script**:  
   Open the Shell tab and run the following command:

```bash
python google_scholar_web_scraping.py > log.txt 2>&1
```

## Troubleshooting (If Running Locally)

This explains how to enable activation if you run into an issue (Steps to Change the Execution Policy):

1. **Open PowerShell as Administrator:**
   Right-click the Start menu and select "Windows PowerShell (Admin)" or "Windows Terminal (Admin)" if you're using Windows 10 or 11.

2. **Check the Current Execution Policy:**
   Run the following command to see your current execution policy:

```bash
Get-ExecutionPolicy
```

3.  **Change Current Execution Policy:**
    If the execution policy is too restrictive (e.g., Restricted), you can change it to RemoteSigned, which allows scripts that you create locally to run, but requires that scripts downloaded from the internet be signed by a trusted publisher.

```bash
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

4.  **Confirm the Change:**
Type Y when prompted.

5.  **Try Activating the Virtual Environment Again: Once the execution policy is changed, you should be able to activate your virtual environment with:

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

## To Do

1. Incorporate Selenium:
   Add Selenium functionality to be able to click "Read more" and handle more than 20 articles.
