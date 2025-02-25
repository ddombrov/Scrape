import os
import time
import pandas as pd
from serpapi import GoogleSearch
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

# File paths
INPUT_YEAR_FILE = "year.txt"
INPUT_URLS_FILE = "urls.txt"
LOG_FILE = "log.txt"
OUTPUT_FILE = "google_scholar_authors.csv"

# Load keyword categories (from keywords.py)
from keywords import (
    conference_keywords, preprint_keywords, journal_keywords,
    book_keywords, book_chapter_keywords, patent_keywords
)

### --- 1. FILE VERIFICATION FUNCTIONS --- ###
def verify_input_files():
    """Verify that required input files exist and are readable."""
    if not os.path.exists(INPUT_YEAR_FILE):
        log_error(f"Error: {INPUT_YEAR_FILE} not found.")
        exit(1)
    if not os.path.exists(INPUT_URLS_FILE):
        log_error(f"Error: {INPUT_URLS_FILE} not found.")
        exit(1)

def get_input_year():
    """Read and return the input year from file."""
    try:
        with open(INPUT_YEAR_FILE, "r") as f:
            input_year = int(f.read().strip())
            since_input_year = input_year - 4  
            return input_year, since_input_year
    except (FileNotFoundError, ValueError):
        log_error("Error: Could not read input year file.")
        exit(1)

def log_error(message, separator=False):
    """Log errors to log.txt for manual inspection with proper formatting."""
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(message + "\n") 
        print(message)  
        if separator:
            log.write("\n" + "-" * 50 + "\n\n")  

### --- 2. URL VERIFICATION FUNCTIONS --- ###
def verify_and_extract_urls():
    """Extract Google Scholar author IDs from URLs and return them."""
    author_urls = {}
    try:
        with open(INPUT_URLS_FILE, "r") as file:
            for line in file:
                url = line.strip()
                if url:
                    parsed_url = urlparse(url)
                    query_params = parse_qs(parsed_url.query)
                    author_id = query_params.get("user", [None])[0]
                    if author_id:
                        author_urls[author_id] = url
                    else:
                        log_error(f"Invalid or missing Scholar ID in URL: {url}") 
    except FileNotFoundError:
        log_error(f"Error: {INPUT_URLS_FILE} not found.")
        exit(1)
    
    if not author_urls:
        log_error("Error: No valid author IDs found.")
        exit(1)

    return author_urls

### --- 3. SCRAPER FUNCTIONS --- ###
def fetch_scholar_data(author_id, start_index=0):
    """Fetch Google Scholar author data with pagination."""
    params = {
        "api_key": API_KEY,
        "engine": "google_scholar_author",
        "author_id": author_id,
        "hl": "en",
        "sort": "pubdate",
        "start": start_index,
        "num": 100,
    }
    try:
        search = GoogleSearch(params)
        return search.get_dict()
    except Exception as e:
        log_error(f"Error fetching data for {author_id}: {e}")
        return None

def scrape_profile_data(results):
    """Extracts author's name and profile details."""
    return results.get("author", {}).get("name")

def scrape_profile_citations(results, input_year, author_name):
    """Extracts total citations, H-index values, and logs missing data."""
    citation_data = results.get("cited_by", {}).get("table", [])
    google_scholar_status, year_citations, h_index_overall, h_index_since = None, None, None, None
    since_year = None  # ✅ Store the correct "Since Year"

    try:
        google_scholar_status = "yes"
        h_index_overall = citation_data[1]["h_index"]["all"]

        # ✅ Extract the correct "Since Year" dynamically
        since_year = citation_data[1]["h_index"].keys() - {"all"}
        since_year = list(since_year)[0] if since_year else None  # Get first available key

        if since_year:
            h_index_since = citation_data[1]["h_index"].get(since_year, None)
        else:
            log_error(f"{author_name}'s profile is missing the 'Since' year for H-Index.", separator=True)

    except (IndexError, KeyError, TypeError) as e:
        log_error(f"Error extracting citation metrics for {author_name}: {e}")

    try:
        citation_graph = results.get("cited_by", {}).get("graph", [])
        for year_data in citation_graph:
            if str(year_data["year"]) == str(input_year):
                year_citations = year_data["citations"]
                break
        if year_citations is None:
            log_error(f"No citation data found for {author_name} in {input_year}.")
    except (KeyError, TypeError) as e:
        log_error(f"Error extracting citations for {author_name} in {input_year}: {e}")

    return google_scholar_status, year_citations, h_index_overall, h_index_since, since_year

def scrape_profile(author_id, author_url, author_name, input_year):
    """Scrape all details from a single author's profile."""
    results = fetch_scholar_data(author_id)
    if results is None:
        log_error(f"Failed to retrieve profile for {author_name} ({author_id})")
        return None

    google_scholar_status, year_citations, h_index_overall, h_index_since, since_year = scrape_profile_citations(
        results, input_year, author_name  # ✅ since_year now extracted inside function
    )

    if h_index_since is None:
        log_error(f"{author_name}'s profile is missing H-Index Since {since_year or 'UNKNOWN'}. Might be new.", separator=True)

    article_counters, missing_year_articles = scrape_articles(author_id, author_name, input_year)

    if sum(article_counters.values()) == 0:
        log_error(f"No articles found for {author_name}. Possible new or inactive profile.", separator=True)

    if missing_year_articles:
        log_error(
            f"{author_name}'s following articles are missing a year and could be in {input_year}–{input_year + 1}:\n" 
            + "\n".join(missing_year_articles),
            separator=True
        )

    return {
        "Full Name": author_name,
        "Google Scholar Profile URL": author_url,
        "Google Scholar": google_scholar_status,
        f"Citations in {input_year}": year_citations,
        "H-Index Overall": h_index_overall,
        f"H-Index Since {since_year or 'UNKNOWN'}": h_index_since,  # ✅ Corrected key
        **article_counters
    }

def scrape_articles(author_id, author_name, input_year):
    """Fetch and process articles, only logging missing years if they fall within the expected range."""
    counters = {
        "Peer Reviewed Articles": 0,
        "Conference Papers": 0,
        "arXiv Preprint": 0,
        "Books": 0,
        "Book Chapters": 0,
        "Patent": 0
    }

    processed_articles = set()
    start_index = 0
    max_attempts = 3  
    missing_year_articles = []  

    may_cutoff = input_year  
    april_cutoff = input_year + 1  

    while max_attempts > 0:
        results = fetch_scholar_data(author_id, start_index)
        if results is None:
            log_error(f"Failed to fetch articles for {author_name} ({author_id}).")
            return counters, missing_year_articles  
        
        publications = results.get("articles", [])

        if not publications:
            return counters, missing_year_articles 

        for pub in publications:
            title = pub.get("title", "").lower()
            source = pub.get("publication", "").lower()
            pub_year = pub.get("year", "").strip()

            if not pub_year.isdigit():
                missing_year_articles.append(f"'{title}'") 
                continue  

            pub_year = int(pub_year)

            if pub_year < may_cutoff or pub_year > april_cutoff:
                continue  

            article_key = f"{title}-{pub_year}"
            if article_key in processed_articles:
                continue
            processed_articles.add(article_key)

            if any(keyword in title or keyword in source for keyword in conference_keywords):
                counters["Conference Papers"] += 1
            elif any(keyword in title or keyword in source for keyword in journal_keywords):
                counters["Peer Reviewed Articles"] += 1
            elif any(keyword in title or keyword in source for keyword in preprint_keywords):
                counters["arXiv Preprint"] += 1
            elif any(keyword in title or keyword in source for keyword in book_keywords):
                counters["Books"] += 1
            elif any(keyword in title or keyword in source for keyword in book_chapter_keywords):
                counters["Book Chapters"] += 1
            elif any(keyword in title or keyword in source for keyword in patent_keywords):
                counters["Patent"] += 1

        start_index += 100
        max_attempts -= 1
        time.sleep(1)

    return counters, missing_year_articles  

def save_to_csv(data, filename):
    """Save extracted data to a CSV file, including totals."""
    df = pd.DataFrame(data)

    # ✅ Convert numeric columns to numeric type (ignore non-numeric columns)
    numeric_cols = df.columns[2:]  # Exclude "Full Name" & "Google Scholar Profile URL"
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # ✅ Compute totals (sum for numeric columns)
    totals = df[numeric_cols].sum(numeric_only=True)

    # ✅ Create "Total" row with empty name & profile link
    total_row = pd.Series(["Total", ""] + totals.tolist(), index=df.columns)

    # ✅ Append the total row to the DataFrame
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    # ✅ Save to CSV
    df.to_csv(filename, encoding="utf-8", index=False)
    print(f"Data saved to {filename}")


### --- 4. MAIN EXECUTION --- ###
if __name__ == "__main__":
    
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write("Google Scholar Scraper Log\n")
        log.write("=" * 50 + "\n\n")

    verify_input_files()
    input_year, since_input_year = get_input_year()
    author_urls = verify_and_extract_urls()

    authors_data = []
    for author_id, url in author_urls.items():
        results = fetch_scholar_data(author_id)
        author_name = scrape_profile_data(results) if results else "Unknown Author"
        profile_data = scrape_profile(author_id, url, author_name, input_year)
        if profile_data:
            authors_data.append(profile_data)

    save_to_csv(authors_data, OUTPUT_FILE)

