from bs4 import BeautifulSoup
import requests
import csv
import time
import random
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from keywords import (conference_keywords, ignored_keywords, citations_keywords,
                      preprint_keywords, journal_keywords, book_keywords,
                      book_chapter_keywords, patent_keywords)

def transform_url(original_url):
    """Transform the given URL to the desired format."""

    if not original_url or not original_url.startswith(('https://scholar.google', 'http://scholar.google')):
        print(
            f"\n\n\n\n\nPROFILE:\nCheckpoint 1: Invalid URL scheme: Bad\nProblematic URL:\n\"{original_url}\"")
        return None
    else:
        print(f"\n\n\n\n\nPROFILE:\nCheckpoint 1: Valid URL scheme:\t\t\t\t\t\t\t\t\tGood")

    parsed_url = urlparse(original_url)
    query_params = parse_qs(parsed_url.query)
    query_params.update({'view_op': ['list_works'], 'sortby': ['pubdate']})
    new_query_params = {
        'hl': query_params.get('hl', [''])[0],
        'user': query_params.get('user', [''])[0],
        'view_op': 'list_works',
        'sortby': 'pubdate'
    }

    new_query_string = urlencode(new_query_params, doseq=True)
    return urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query_string,
        parsed_url.fragment
    ))


def extract_google_scholar_name(doc, url):
    """
    Extracts the full name of the Google Scholar profile from the provided HTML document.

    Args:
        doc (BeautifulSoup): The parsed HTML document.
        url (str): The URL of the Google Scholar profile, used for error logging.

    Returns:
        str: The extracted full name if found, otherwise "Unknown".
    """
    name = doc.find(id="gsc_prf_in")
    if name:
        print(f"Checkpoint 3: Name was located:\t\t\t\t\t\t\t\t\tGood")
        return name.string
    else:
        print(
            f"Checkpoint 3: Name was not located: Bad\nProblematic URL:\n\"{url}\"")
        return "Unknown"


def extract_h_index_values(doc, url):
    """
    Extracts the h-index values (overall and since) from the provided HTML document.

    Args:
        doc (BeautifulSoup): The parsed HTML document.
        url (str): The URL of the Google Scholar profile, used for error logging.

    Returns:
        tuple: A tuple containing the h-index overall and h-index since values, or (None, None) if not found.
    """
    h_index = doc.find_all(string="h-index")
    if h_index:
        parent = h_index[0].parent.parent.parent
        td_elements = parent.find_all('td')
        h_index_overall = td_elements[-2].get_text(strip=True)
        h_index_since = td_elements[-1].get_text(strip=True)
        print(f"Checkpoint 4: H-indices found:\t\t\t\t\t\t\t\t\tGood")
        return h_index_overall, h_index_since
    else:
        print(
            f"Checkpoint 4: H-indices not found: Bad\nProblematic URL:\n\"{url}\"")
        return None, None


def extract_article_urls(doc, url):
    """
    Extracts article URLs from the provided HTML document.

    Args:
        doc (BeautifulSoup): The parsed HTML document.
        url (str): The URL of the Google Scholar profile, used for error logging.

    Returns:
        list: A list of article URLs extracted from the document, or an empty list if none are found.
    """
    article_urls = []
    base_url = 'https://scholar.google.ca'
    parent_element = doc.find(id='gsc_a_b')

    if parent_element:
        children = parent_element.find_all(class_='gsc_a_tr')
        for child in children:
            grandchildren = child.find_all(class_='gsc_a_t')
            for grandchild in grandchildren:
                articles = grandchild.find_all('a', href=True)
                for article in articles:
                    href = article['href']
                    if href.startswith('/'):
                        href = base_url + href
                    if href:
                        article_urls.append(href)

    # Check if article URLs were found
    if article_urls:
        print(f"Checkpoint 5: Article URL data found:\t\t\t\t\t\t\tGood")
    else:
        print(
            f"Checkpoint 5: Article URL data not found: Bad\nProblematic URL:\n\"{url}\"")

    return article_urls


def scrape_profile(url):
    """Function to scrape data from a profile"""

    url = transform_url(url)

    # Check if the URL is empty
    if not url:
        print(
            f"Checkpoint 2: URL data is empty: Bad\nProblematic URL:\n\"{url}\"")
        return None
    else:
        print(f"Checkpoint 2: URL data is not empty:\t\t\t\t\t\t\tGood")

    # Set the headers for the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:

        # Send a GET request to the URL
        result = requests.get(url, headers=headers)
        result.raise_for_status()
        doc = BeautifulSoup(result.text, 'html.parser')

        # Initialize the profile data
        profile_data = {}

        profile_data['Full Name'] = extract_google_scholar_name(doc, url)

        profile_data['H-Index Overall'], profile_data['H-Index Since'] = extract_h_index_values(
            doc, url)

        article_urls = extract_article_urls(doc, url)

        # Initialize counters
        counters = {
            'Citation Count': 0,
            'Peer Reviewed Articles': 0,
            'arXiv Preprint': 0,
            'Books': 0,
            'Book Chapters': 0,
            'Conference Papers': 0,
            'Patent': 0
        }
        article_number = 0

        # Process each article URL
        for article_url in article_urls:
            time.sleep(2)  # Rate limit
            article_number += 1
            return_status = 1
            old_counters = counters.copy()
            counters, return_status = scrape_article(article_url, counters)

            # If the valid articles have all been processed, break the loop
            if return_status == 0:
                break

            elif return_status == 1:

                # If more than 20 articles are found, manual inspection is required
                if article_number == 20:
                    print(
                        f"\nMANUAL INSPECTION REQUIRED:\nMore than 20 articles found: Bad\nProblematic profile URL:\n{url}\n")

                # In the case the count was supposed to go up and didn't, manual inspection is required
                if counters == old_counters:
                    print(
                        f"\nMANUAL INSPECTION REQUIRED:\nNo counts updated: Bad\nProblematic URL:\n{article_url}\n")

                print("\nNew Counts:\n", counters, "\n")

            # If the date format is invalid, manual inspection is required
            elif return_status == 2:
                counters = old_counters
                print(
                    f"\nMANUAL INSPECTION REQUIRED:\nDate format invalid: Bad\nProblematic URL:\n{article_url}\n")

            # If there is an error fetching data from the article, manual inspection is required
            elif return_status == 3:
                counters = old_counters
                print(
                    f"\nMANUAL INSPECTION REQUIRED:\nError fetching data from article: Bad\nProblematic URL:\n{article_url}\n")

            # If an unrecognized article_field is found, manual inspection is required
            elif return_status == 4:
                counters = old_counters
                print(
                    f"\nMANUAL INSPECTION REQUIRED:\nUnrecognized article_field: Bad\nProblematic URL:\n{article_url}\n")

            # If no 'Cited by' number is found, manual inspection is required
            elif return_status == 5:
                counters = old_counters
                print(
                    f"\nMANUAL INSPECTION REQUIRED:\nNo 'Cited by' number found: Bad\nProblematic URL:\n{article_url}\n")

            # If the publication date is not in the correct range, manual inspection is required
            elif return_status == 6:
                counters = old_counters

        # Add the counters to the profile data
        for key, value in counters.items():
            profile_data[key] = value

        print(f"\nCheckpoint 6: Returned after scraping from profile:\tGood\n")

        return profile_data

    except requests.RequestException as e:
        print(
            f"Checkpoint 6: Error fetching data from profile and/or articles: Bad\nProblematic URL:\n\"{e}\"")
        return None


def process_date(date):
    """
    Processes a date string and extracts the year and month.

    Args:
        date (str): The date string in the format 'YYYY/MM/DD' or 'YYYY/MM'.

    Returns:
        tuple: A tuple containing the year and month as integers.
               If the date format is invalid or the date is None, returns (None, None).
    """
    if date and date.count('/') == 2:
        year, month, _ = date.split('/')
        return int(year), int(month)

    if date and date.count('/') == 1:
        year, month = date.split('/')
        return int(year), int(month)

    return None, None


def validate_publication_date(year, month, input_year):
    """
    Validates the publication date against the input year and range requirements.

    Args:
        year (int): The publication year of the article.
        month (int): The publication month of the article.
        input_year (int): The year against which to validate the publication date.

    Returns:
        int: A status code representing the validation result:
             - 0: If the publication date is before the input year.
             - 6: If the publication date is not in the correct range.
             - 1: If the publication date is valid and in the correct range.
    """
    # Check if the publication date is before the input year
    if (year < input_year or (year == input_year and month < 5)):
        return 0

    # Check if the publication date is in the correct range
    if not ((year == input_year and month >= 5) or (year == input_year + 1 and month < 5)):
        print(f"Checkpoint 8: Publication date is not in the correct range:\t\tArticle skipped")
        return 6

    print(f"Checkpoint 8: Publication date is in the correct range:\t\t\tArticle accepted")
    return 1


def scrape_article(article_url, counters):
    """Function to scrape an article"""

    if not article_url:
        return counters, 3

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:

        # Send a GET request to the URL
        result = requests.get(article_url, headers=headers)
        result.raise_for_status()
        doc = BeautifulSoup(result.text, 'html.parser')

        # Extract the publication date
        fields = doc.find_all('div', class_='gsc_oci_field')
        values = doc.find_all('div', class_='gsc_oci_value')
        date = None

        for field, value in zip(fields, values):
            if field.string and 'publication date' in field.string.strip().lower():
                date = value.string.strip() if value.string else value.get_text(strip=True)
                break

        year, month = process_date(date)
        if year is None or month is None:
            return counters, 2

        status_code = validate_publication_date(year, month, input_year)
        if status_code != 1:
            return counters, status_code

        # Process each field and value
        for field, value in zip(fields, values):
            article_field = field.string.lower().strip()

            # Handle citations-related keywords
            if any(keyword in article_field for keyword in citations_keywords):
                if value:
                    match = re.search(r'Cited by (\d+)', str(value))
                    if match:
                        cited_by_number = match.group(1)
                        counters['Citation Count'] += int(cited_by_number)

                    # If no 'Cited by' number is found, manual inspection is required
                    else:
                        return counters, 5

            # Check for ignored fields
            if any(ignored_keyword in article_field for ignored_keyword in ignored_keywords):
                continue

            # Handle conference-related keywords
            elif any(keyword in article_field for keyword in conference_keywords) or (value and any(keyword in str(value) for keyword in conference_keywords)):
                counters['Conference Papers'] += 1
                continue

            # Handle preprint-related keywords
            elif value and any(keyword in str(value) for keyword in preprint_keywords):
                counters['arXiv Preprint'] += 1
                continue

            # Handle journal-related keywords
            elif any(keyword in article_field for keyword in journal_keywords) and 'preprint' not in str(value):
                counters['Peer Reviewed Articles'] += 1
                continue

            # Handle book-related keywords
            elif any(keyword in article_field for keyword in book_keywords):
                counters['Books'] += 1

                # Check if the next field is 'book chapter' and has pages
                next_field_index = fields.index(field) + 1
                if next_field_index < len(fields):
                    next_article_field = fields[next_field_index].string.lower(
                    ).strip()
                    next_value = values[next_field_index]

                    # Check if the next field is a book chapter and only count it as a book chapter
                    if any(keyword in next_article_field for keyword in book_chapter_keywords) and str(next_value):
                        counters['Book Chapters'] += 1
                        counters['Books'] -= 1
                continue

            # Handle patent-related keywords
            elif any(keyword in article_field for keyword in patent_keywords):
                counters['Patent'] += 1
                continue

            # Handle cases that don't match any known keyword
            if not (any(keyword in article_field for keyword in (citations_keywords | preprint_keywords | journal_keywords | conference_keywords | book_keywords | patent_keywords)) or
                    any(keyword in str(value) for keyword in (conference_keywords | preprint_keywords))):
                return counters, 4

        print(f"Checkpoint 7: Article was scraped successfully:\t\t\t\t\tGood")
        return counters, 1

    except requests.RequestException as e:
        print(
            f"Checkpoint 7: Error fetching data from article: Bad\nProblematic URL:\n\"{e}\"")
        return counters, 3


def process_urls(input_file, output_file):
    """Function to process a list of URLs"""

    since_input_year = input_year - 4

    # Read the URLs from the input file
    with open(input_file, 'r') as file:
        urls = file.read().splitlines()

    # Write the header row to the CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Full Name', 'Link', 'Google Scholar',
            f'Citation Count {input_year}',
            f'H-Index Since {since_input_year}', 'H-Index Overall',
            f'Peer Reviewed Articles {input_year}',
            f'arXiv Preprint {input_year}',
            f'Books {input_year}',
            f'Book Chapters {input_year}',
            f'Conference Papers {input_year}',
            f'Patent {input_year}',
            'Total Citations',
            f'Average Citations per Researcher in {input_year}',
            f'Average H-Index Since {since_input_year} per Researcher',
            'Average Overall H-Index',
            'Total Peer Reviewed Articles',
            'Average Peer Reviewed Publications per Researcher',
            'Total Conference Papers'
        ])

        print("PROCESS HAS BEGUN SCRAPING")

        # Process each URL
        for url in urls:
            time.sleep(random.uniform(1, 3))
            profile_data = scrape_profile(url)

            if profile_data:
                writer.writerow([
                    profile_data.get('Full Name', ''),
                    url,
                    "Yes",
                    profile_data.get('Citation Count', ''),
                    profile_data.get('H-Index Since', ''),
                    profile_data.get('H-Index Overall', ''),
                    profile_data.get('Peer Reviewed Articles', ''),
                    profile_data.get('arXiv Preprint', ''),
                    profile_data.get('Books', ''),
                    profile_data.get('Book Chapters', ''),
                    profile_data.get('Conference Papers', ''),
                    profile_data.get('Patent', ''),
                ])

    print("\n\nPROCESS COMPLETED SUCCESSFULLY\n\n")


input_file = 'urls.txt'  # File containing list of URLs
output_file = 'output.csv'  # File to save the results
input_year = 2023  # Year to extract (ex. put 2023 for May 2023 - April 2024)

# Run the process
process_urls(input_file, output_file)
