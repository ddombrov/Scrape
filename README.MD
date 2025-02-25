# Google Scholar Bibliometrics Web Scraper

## Summary
This project scrapes Google Scholar Bibliometrics data using Python, allowing you to collect H-index, citations, and other scholarly metrics for researchers.

## Getting Started (Simple - Run Online)

1. **Go to** [Replit](https://replit.com)
2. **Click “Import from GitHub”**
3. **Paste this URL**:  
   ```
   https://github.com/ddombrov/Scrape.git
   ```
4. **Click “Import”**  
   Replit will set up the project automatically.
5. **Edit the Input Files**  
   - Open `urls.txt` and add Google Scholar profile URLs (one per line).
   - Open `year.txt` and enter the year you want to scrape.
6. **Set Your API Key** (See "API Key Setup" below)
7. **Run the Scraper**  
   Click the "Run" button or open the Shell and type:
   ```
   python google_scholar_scraper.py
   ```

## 🛠 Getting Started (Local - Full Control)

### **1. Install Python**
Run the following command **based on your operating system**:

- **Windows (Run in Command Prompt as Admin)**
```
winget install Python.Python.3.11
```
Mac (Run in Terminal)
```
brew install python
```

Linux (Debian/Ubuntu)
```
sudo apt update && sudo apt install python3 python3-pip -y
```

### **2. Download the Scraper**
Fork: https://github.com/ddombrov/Scrape.git.
Then clone your forked repo.
Open a terminal or command prompt and run:
```bash
cd Scrape
```

### **3. Install Required Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Edit the Input Files**  
   - Open `urls.txt` and add Google Scholar profile URLs (one per line).
   - Open `year.txt` and enter the year you want to scrape.

### **5. Set Your API Key** (See "API Key Setup" below)

### **6. Run the Scraper**
```
python google_scholar_scraper.py
```

## 🔑 API Key Setup (Required)

This scraper uses **SerpAPI** to fetch data. You must set up an **API key**.

### **1. Get an API Key**
- **Sign up** at [SerpAPI](https://serpapi.com/)
- **Find your API key** in your account settings.

### **2. Save the API Key**
- Inside the `Scrape` folder, create a new file named `.env`
- Add the following line (replace `YOUR_API_KEY` with the one the website gives you):
  ```
  API_KEY=YOUR_API_KEY
  ```
- **Save the file** and **do not rename it**.

## 📊 Viewing the Results

After running the scraper, you’ll get two files:

1. **`google_scholar_authors.csv`** (main output)  
   - Open in **Excel** or **Google Sheets** to see the collected data.

2. **`log.txt`** (issues & errors)  
   - This file logs problems like missing data or invalid profiles.
   - If a profile is missing an H-index or if an article has no year, it will be listed here.

---

## ❓ Troubleshooting

### **1. `API_KEY not found` Error**
- Ensure your `.env` file is in the **same folder as the script**.
- Check that `.env` contains:
  ```
  API_KEY=YOUR_API_KEY
  ```

### **2. `Permission Denied` Error (Mac/Linux Users)**
If you see a **permission error**, try:

```
chmod +x google_scholar_web_scraping.py
```

### **3. `Too Many Requests` Error (SerpAPI Blocked You)**
- **Wait** 1-2 hours and try again.
- **Reduce the number of URLs** in `urls.txt`.
- **Use a different API key** (new SerpAPI account).


## 📧 Contact
For questions, contact **Daniel Dombrovsky** at `ddombrov@uoguelph.ca`.
