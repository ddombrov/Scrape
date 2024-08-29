from bs4 import BeautifulSoup
import requests
import csv
import time
import random
import re
import sys
import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from keywords import (conference_keywords, ignored_keywords, citations_keywords,
                      preprint_keywords, journal_keywords, book_keywords,
                      book_chapter_keywords, patent_keywords)
sys.stdout.reconfigure(encoding='utf-8')


def is_file_empty(file_path):
    return os.path.getsize(file_path) == 0


def get_final_url(url):
    """
    Function to follow a URL redirection and return the final URL.
    Args:
        url (str): The original URL.
    Returns:
        str: The final URL after all redirects.
    """
    try:
        # Send a GET request and allow redirects
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
        final_url = response.url

        # Check if the final URL is different from the original one
        if final_url != url:
            print(f"URL has been redirected: {url} -> {final_url}")
        else:
            print(f"No redirection detected for URL: {url}")

        return final_url
    except requests.RequestException as e:
        print(f"Error fetching final URL: {e}")
        return None


def determine_year(input_year_file):
    """Function to determine the year to extract from the Google Scholar profiles"""

    try:
        with open(input_year_file, 'r') as file:
        
            year = file.read()
            if year:
                int(year.strip())

            if not year:
                manual_inspection_required(
                    "Invalid year data", "input year file", input_year_file)
                return None

            year = int(year)

            if test_mode:
                print(f"Checkpoint 1: Year data found:\t\t\t\t\t\t\t\t\t\tGood")

            return year

    except FileNotFoundError:
        manual_inspection_required(
            "Year data not found", "input year file", input_year_file)
        return None


def update_summary(summary_data, profile_data):

    # if profile_data is not None:

    # Extract data from the profile
    # total_citations = int(profile_data.get(
    #     'Citation Count of Year Period', 0))
    # h_index_since = int(profile_data.get('H-Index Since', 0))
    # h_index_overall = int(profile_data.get('H-Index Overall', 0))
    # peer_reviewed_articles = int(
    #     profile_data.get('Peer Reviewed Articles', 0))
    # conference_papers = int(profile_data.get('Conference Papers', 0))

    if summary_data is not None and profile_data is not None:

        # Update the summary data
        summary_data['total_citations'] += int(
            profile_data.get('Total Citations of the Profile', 0))
        summary_data['total_h_index_since'] += int(
            profile_data.get('H-Index Since', 0))
        summary_data['total_h_index_overall'] += int(
            profile_data.get('H-Index Overall', 0))
        summary_data['total_peer_reviewed_articles'] += int(
            profile_data.get('Peer Reviewed Articles', 0))
        summary_data['total_conference_papers'] += int(
            profile_data.get('Conference Papers', 0))
        summary_data['num_profiles'] += 1


def check_input_file(input_file):

    try:
        with open(input_file, 'r') as file:
            if is_file_empty(input_file):
                manual_inspection_required(
                    "File is empty", "input file", input_file)
                exit("Program will now exit")

            if test_mode:
                print(f"Checkpoint 0: File is not empty:\t\t\t\t\t\t\t\t\t\tGood")
            
            return True
        
    except FileNotFoundError:
        manual_inspection_required(
            "A file was not found", "input file", input_file)
        exit("Program will now exit")


def process_urls(input_urls_file, output_spreadsheet_file):
    """Function to process a list of URLs"""

    # Read the URLs from the input file
    with open(input_urls_file, 'r') as file:
        urls = file.read().splitlines()

    # Write the header row to the CSV file
    with open(output_spreadsheet_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Full Name', 'Link', 'Google Scholar',
            f'Citation Count of Year Period {input_year}',
            f'H-Index Since {since_input_year}', 'H-Index Overall',
            f'Peer Reviewed Articles {input_year}',
            f'arXiv Preprint {input_year}',
            f'Books {input_year}',
            f'Book Chapters {input_year}',
            f'Conference Papers {input_year}',
            f'Patent {input_year}',
            'Total Citations of the Profile',
            'Year Period Citations of all Profiles',
            'Total Citations of all Profiles',
            f'Average Citations per Researcher in {input_year}',
            f'Average H-Index Since {since_input_year} per Researcher',
            'Average Overall H-Index',
            'Total Peer Reviewed Articles',
            'Average Peer Reviewed Publications per Researcher',
            'Total Conference Papers'
        ])

        summary_data = {
            'total_citations': 0,
            'total_h_index_since': 0,
            'total_h_index_overall': 0,
            'total_peer_reviewed_articles': 0,
            'total_conference_papers': 0,
            'num_profiles': 0
        }

        if test_mode:
            print("PROCESS HAS BEGUN SCRAPING")

        for url in urls:
            profile_data = process_url(url, writer)
            update_summary(summary_data, profile_data)

        create_summary(summary_data)

    if test_mode:
        print("\n\nPROCESS COMPLETED SUCCESSFULLY\n\n")


def process_url(url, writer):
    """Function to process and scrape data for a single URL and write to CSV."""

    time.sleep(random.uniform(sleep_time_minimum, sleep_time_maximum))
    profile_data = scrape_profile(url)

    if profile_data is not None:
        writer.writerow([
            str(profile_data.get('Full Name', '')).encode(
                'utf-8', 'ignore').decode('utf-8'),
            str(url).encode('utf-8', 'ignore').decode('utf-8'),
            "Yes",
            str(profile_data.get('Citation Count of Year Period', '')).encode(
                'utf-8', 'ignore').decode('utf-8'),
            str(profile_data.get('H-Index Since', '')
                ).encode('utf-8', 'ignore').decode('utf-8'),
            str(profile_data.get('H-Index Overall', '')
                ).encode('utf-8', 'ignore').decode('utf-8'),
            str(profile_data.get('Peer Reviewed Articles', '')).encode(
                'utf-8', 'ignore').decode('utf-8'),
            str(profile_data.get('arXiv Preprint', '')).encode(
                'utf-8', 'ignore').decode('utf-8'),
            str(profile_data.get('Books', '')).encode(
                'utf-8', 'ignore').decode('utf-8'),
            str(profile_data.get('Book Chapters', '')).encode(
                'utf-8', 'ignore').decode('utf-8'),
            str(profile_data.get('Conference Papers', '')).encode(
                'utf-8', 'ignore').decode('utf-8'),
            str(profile_data.get('Patent', '')).encode(
                'utf-8', 'ignore').decode('utf-8'),
            str(profile_data.get('Total Citations of the Profile', '')).encode(
                'utf-8', 'ignore').decode('utf-8'),
        ])

        return profile_data


def manual_inspection_required(issue, location_type, location):
    print(
        f"MANUAL INSPECTION REQUIRED:\n{issue}: Bad\nProblematic {location_type}:\n{location}\n\n")


def scrape_profile(url):
    """Function to scrape data from a profile"""

    # Get the final URL after following any redirects
    final_url = get_final_url(url)

    # If final URL is None, manual inspection is required
    if not final_url:
        manual_inspection_required(
            "Unable to resolve final URL", "profile URL", url)
        return None

    url = transform_url(url)

    # Check if the URL is empty
    if not url:
        manual_inspection_required("URL data is empty", "profile URL", url)
        return None
    else:
        if test_mode:
            print(f"Checkpoint 3: URL data is not empty:\t\t\t\t\t\t\tGood")

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
        profile_data = {
            'Full Name': extract_google_scholar_name(doc, url),
            'H-Index Overall': None,
            'H-Index Since': None,
            'Citation Count of Year Period': None,
            'Total Citations of the Profile': None
        }
        full_name = profile_data.get('Full Name', '')
        print(f"\n*********************************************************")
        print(f"Full name scan for {full_name} has started.")
        print(f"*********************************************************\n")

        profile_data['H-Index Overall'], profile_data['H-Index Since'] = extract_h_index_values(
            doc, url)
        profile_data['Citation Count of Year Period'] = extract_citation_count_of_year(
            doc, url)
        profile_data['Total Citations of the Profile'] = extract_total_citation_count(
            doc, url)
        article_urls = extract_article_urls(doc, url)

        # Initialize counters
        counters = {
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

            time.sleep(random.uniform(sleep_time_minimum, sleep_time_maximum))
            article_number += 1
            return_status = 1
            old_counters = counters.copy()
            counters, return_status = scrape_article(article_url, counters)

            # If more than 20 articles are found, manual inspection is required
            if article_number == 20:
                manual_inspection_required(
                    "More than 20 articles found (first 20 have been examined, the rest you will need to examine manually)", "profile URL", url)

            # If the valid articles have all been processed, break the loop
            if return_status == 0:
                break

            # In the case the count was supposed to go up and didn't, manual inspection is required
            elif return_status == 1 and counters == old_counters:
                manual_inspection_required(
                    "No counts updated", "article URL", article_url)

                if test_mode:
                    print("\nNew Counts:\n", counters, "\n")

            # If the date format is invalid, manual inspection is required
            elif return_status == 2:
                manual_inspection_required(
                    "Date format invalid", "article URL", article_url)

            # If there is an error fetching data from the article, manual inspection is required
            elif return_status == 3:
                manual_inspection_required(
                    "Error fetching data from article", "article URL", article_url)

            # If an unrecognized article_field is found, manual inspection is required
            elif return_status == 4:
                manual_inspection_required(
                    "Unrecognized article_field (type of article could not be dertermined so article was skipped)", "article URL", article_url)

            # If the article had an issue/skipped then revert to the old counters
            elif return_status == 2 or return_status == 3 or return_status == 4 or return_status == 5:
                counters = old_counters

        # Add the counters to the profile data
        for key, value in counters.items():
            profile_data[key] = value

        if test_mode:
            print(f"\nCheckpoint 7: Returned after scraping from profile:\tGood\n")

        full_name = profile_data.get('Full Name', '')
        print(f"*********************************************************")
        print(f"Full name scan for {full_name} is complete.")
        print(f"*********************************************************")

        return profile_data

    except requests.RequestException as e:
        manual_inspection_required("Error fetching data", "article/profile", e)
        return None


def transform_url(original_url):
    """Transform the given URL to the desired format."""

    if not original_url or not original_url.startswith(('https://scholar.google', 'http://scholar.google')):
        manual_inspection_required(
            "Invalid URL scheme", "profile URL", original_url)
        return None
    else:
        if test_mode:
            print(
                f"\n\n\n\n\nPROFILE:\nCheckpoint 2: Valid URL scheme:\t\t\t\t\t\t\t\t\tGood")

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
        if test_mode:
            print(f"Checkpoint 4: Name was located:\t\t\t\t\t\t\t\t\tGood")
        return name.string
    else:
        manual_inspection_required("Name was not located", "profile URL", url)
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
        if test_mode:
            print(f"Checkpoint 5: H-indices found:\t\t\t\t\t\t\t\t\tGood")
        return h_index_overall, h_index_since
    else:
        manual_inspection_required("H-indices not found", "profile URL", url)
        return None, None


def extract_citation_count_of_year(doc, url):
    """
    Extracts the citation count for a given year from a Google Scholar document.
    Parameters:
    - doc: BeautifulSoup object representing the HTML document of the Google Scholar page.
    - url: URL of the Google Scholar page.
    Returns:
    - The citation count for the given year if it exists, otherwise None.
    """

    # Extract years and values
    years = [span.get_text()
             for span in doc.find_all('span', class_='gsc_g_t')]
    values = [a.find('span', class_='gsc_g_al').get_text()
              for a in doc.find_all('a', class_='gsc_g_a')]

    # Find the value of the year
    year_index = years.index(str(input_year)) if str(
        input_year) in years else None
    year_value = values[year_index]

    if year_index is not None and year_index < len(values):
        if test_mode:
            print(f"Checkpoint 10: Citation count data found:\t\t\t\t\t\t\tGood")
        return year_value
    else:
        manual_inspection_required(
            "Citation count data not found", "profile URL", url)
        return None


def extract_total_citation_count(doc, url):
    """
    Extracts the total citation count from a Google Scholar document.
    Parameters:
    - doc: BeautifulSoup object representing the HTML document of the Google Scholar page.
    - url: URL of the Google Scholar page.
    Returns:
    - The citation count for the given year if it exists, otherwise None.
    """

    total_value = doc.find_all(string="Citations")
    if total_value:
        parent = total_value[0].parent.parent.parent
        td_elements = parent.find_all('td')
        total_value = td_elements[-2].get_text(strip=True)
        if test_mode:
            print(
                f"Checkpoint 11: Total citation count data found:\t\t\t\t\t\t\t\t\tGood")
        return total_value
    else:
        manual_inspection_required(
            "Total citation count data not found", "profile URL", url)
        return total_value


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
        if test_mode:
            print(f"Checkpoint 6: Article URL data found:\t\t\t\t\t\t\tGood")
    else:
        manual_inspection_required(
            "Article URL data not found", "article URL", url)

    return article_urls


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

        year, month = process_date(fields, values, date)

        if year is None or month is None:
            return counters, 2

        status_code = validate_publication_date(year, month, input_year)

        if status_code != 1:
            return counters, status_code

        return process_article_fields(fields, values, counters)

    except requests.RequestException as e:
        manual_inspection_required(
            "Error fetching data from article", "article URL", e)
        return counters, 3


def process_date(fields, values, date):
    """
    Processes the publication date of an article.
    """

    for field, value in zip(fields, values):
        if field.string and 'publication date' in field.string.strip().lower():
            date = value.string.strip() if value.string else value.get_text(strip=True)
            break

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
             - 5: If the publication date is not in the correct range.
             - 1: If the publication date is valid and in the correct range.
    """
    # Check if the publication date is before the input year
    if (year < input_year or (year == input_year and month < 5)):
        return 0

    # Check if the publication date is in the correct range
    if not ((year == input_year and month >= 5) or (year == input_year + 1 and month < 5)):
        if test_mode:
            print(
                f"Checkpoint 9: Publication date is not in the correct range:\t\tArticle skipped")
        return 5

    if test_mode:
        print(
            f"Checkpoint 9: Publication date is in the correct range:\t\t\tArticle accepted")
    return 1


def process_article_fields(fields, values, counters):
    """
    Processes fields and values from an article and updates the counters.

    Args:
        fields (list): List of field elements from the article.
        values (list): List of value elements from the article.
        counters (dict): Dictionary of counters to be updated.

    Returns:
        tuple: A tuple containing the updated counters and a status code.
    """
    for field, value in zip(fields, values):
        article_field = field.string.lower().strip()

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
        elif any(keyword in article_field for keyword in journal_keywords) and 'preprint' not in str(value).lower():
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

    if test_mode:
        print(f"Checkpoint 8: Article was scraped successfully:\t\t\t\t\tGood")
    return counters, 1


def create_summary(summary_data):
    num_profiles = summary_data['num_profiles']

    # Calculate averages
    average_citations_per_researcher = summary_data['total_citations'] / \
        num_profiles if num_profiles else 0
    average_h_index_since = summary_data['total_h_index_since'] / \
        num_profiles if num_profiles else 0
    average_overall_h_index = summary_data['total_h_index_overall'] / \
        num_profiles if num_profiles else 0
    average_peer_reviewed_publications = summary_data['total_peer_reviewed_articles'] / \
        num_profiles if num_profiles else 0

    # Write the header row to the CSV file
    with open(output_summary_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Total Citations of all Profiles',
            f'Average Citations per Researcher in {input_year}',
            f'Average H-Index Since {since_input_year} per Researcher',
            'Average Overall H-Index',
            'Total Peer Reviewed Articles',
            'Average Peer Reviewed Publications per Researcher',
            'Total Conference Papers'
        ])

        # Write the calculated data to the CSV
        writer.writerow([
            summary_data['total_citations'],
            average_citations_per_researcher,
            average_h_index_since,
            average_overall_h_index,
            summary_data['total_peer_reviewed_articles'],
            average_peer_reviewed_publications,
            summary_data['total_conference_papers']
        ])


test_mode = False  # Set to True to enable test mode
output_spreadsheet_file = 'output.csv'  # File to save the results
output_summary_file = 'summary.csv'  # File to save the summary
sleep_time_minimum = 1  # Minimum sleep time in seconds
sleep_time_maximum = 3  # Maximum sleep time in seconds

input_urls_file = 'urls.txt' 
input_year_file = 'year.txt'
check_input_file(input_urls_file)
check_input_file(input_year_file)

input_year = determine_year(input_year_file)
since_input_year = input_year - 4

# Run the process
process_urls(input_urls_file, output_spreadsheet_file)
