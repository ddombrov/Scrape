from bs4 import BeautifulSoup
import requests
import csv
import time
import random
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re


def transform_url(original_url):
    """Transform the given URL to the desired format."""

    if not original_url or not original_url.startswith(('http://', 'https://')):
        print(
            f"PROFILE:\nCheckpoint 1: Invalid URL scheme: Bad\nProblematic URL: \"{original_url}\"")
        return None
    else:
        print(f"PROFILE:\nCheckpoint 1: Valid URL scheme: Good")

    # Parse the original URL
    parsed_url = urlparse(original_url)

    # Extract query parameters
    query_params = parse_qs(parsed_url.query)

    # Add or update parameters
    query_params['view_op'] = ['list_works']
    query_params['sortby'] = ['pubdate']

    # Construct the new query string, ensuring the order of parameters
    new_query_params = {
        'hl': query_params.get('hl', [''])[0],
        'user': query_params.get('user', [''])[0],
        'view_op': 'list_works',
        'sortby': 'pubdate'
    }

    # Construct the new query string
    new_query_string = urlencode(new_query_params, doseq=True)

    # Construct the new URL
    new_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query_string,
        parsed_url.fragment
    ))

    return new_url


def scrape_profile(url):
    """Function to scrape data from a profile"""

    url = transform_url(url)

    # Check if the URL is empty
    if not url:
        print(
            f"Checkpoint 2 URL data is empty: Bad\nProblematic URL: \"{url}\"")
        return None
    else:
        print(f"Checkpoint 2 URL data is not empty: Good")

    # Set the headers for the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Send a GET request to the URL
        result = requests.get(url, headers=headers)
        result.raise_for_status()
        doc = BeautifulSoup(result.text, 'html.parser')

        # Extract profile data
        profile_data = {}

        # Find the name of the Google Scholar
        name = doc.find(id="gsc_prf_in")

        if name:
            profile_data['Full Name'] = name.string
            print(f"Checkpoint 3 Name was located: Good")
        else:
            profile_data['Full Name'] = "Unknown"
            print(
                f"Checkpoint 3: Name was not located: Bad\nProblematic URL: \"{url}\"")

        # Extract h-index values
        h_index = doc.find_all(string="h-index")
        if h_index:
            parent = h_index[0].parent.parent.parent
            td_elements = parent.find_all('td')
            profile_data['H-Index Overall'] = td_elements[-2].get_text(
                strip=True)
            profile_data['H-Index Since'] = td_elements[-1].get_text(
                strip=True)
            print(f"Checkpoint 3: Good (h-indices found)")
        else:
            print(
                f"Checkpoint 3: No data for {url} found: H-indices not found.")
            profile_data['H-Index Overall'] = profile_data['H-Index Since'] = None

        # Extract article URLs
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

        if article_urls:
            print(f"Checkpoint 5: Article url data found: Good")
        else:
            print(f"Checkpoint 5: Article url data not found: Bad\nProblematic URL: \"{url}\"")

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
        i = 0

        # Process each article URL
        for article_url in article_urls:
            time.sleep(2)  # Rate limit
            i += 1
            keepGoing = True
            counters, keepGoing = scrape_article(article_url, counters)

            if keepGoing == False:
                break

        # Add total citations to profile data
        profile_data['Total Citations'] = counters['Citation Count']

        # Add the counters to the profile data
        for key, value in counters.items():
            profile_data[key] = value

        print(f"\n\nCheckpoint 4: Profile and articles were scraped successfully: Good")

        return profile_data

    except requests.RequestException as e:
        print(
            f"Checkpoint 4: Error fetching data from profile and/or articles: Bad\nProblematic URL: \"{e}\"")
        return None


def scrape_article(url, counters):
    """Function to scrape an article"""

    if not url:
        print(f"\nARTICLE:\nCheckpoint 6: No data for the article url found: Bad\nProblematic URL: \"{url}\"")
        return counters, True
    else:
        print(f"\nARTICLE:\nCheckpoint 6: Data found for the article url: Good")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        result = requests.get(url, headers=headers)
        result.raise_for_status()
        doc = BeautifulSoup(result.text, 'html.parser')

        fields = doc.find_all('div', class_='gsc_oci_field')
        values = doc.find_all('div', class_='gsc_oci_value')

        date = None
        for field, value in zip(fields, values):
            if field.string and 'publication date' in field.string.strip().lower():
                date = value.string.strip() if value.string else value.get_text(strip=True)
                break

        if date:
            print(f"Checkpoint 8: Date found: Good")
            if date.count('/') == 2:
                year, month, day = date.split('/')
                year = int(year)
                month = int(month)
                print(f"Checkpoint 9: Date has valid format: Good")
            elif date.count('/') == 1:
                year, month, = date.split('/')
                year = int(year)
                month = int(month)
                print(f"Checkpoint 9: Date has valid format: Good")
            else:
                print(
                    f"\nMANUAL INSPECTION REQUIRED:\nCheckpoint 9: Date has invalid format: Bad\nProblematic URL: {url}")
                return counters, True

        else:
            print(
                f"Checkpoint 8: No date found: Bad\nProblematic URL: \"{url}\"")
            return counters, True

        # Check if the publication date is before the input year
        if (year < input_year or (year == input_year and month < 5)):
            print(
                f"Checkpoint 10: Publication date is before May {input_year}: Article skipped")
            return counters, False

        print(f"Checkpoint 10: Publication date is after May {input_year}: Article accepted")

        # Check if the publication date is in the correct range
        if not (year == input_year and month >= 5 or year == input_year + 1 and month < 5):
            print(
                f"Checkpoint 11: Publication date is not in the correct range: Article skipped")
            return counters, True

        print(f"Checkpoint 11: Publication date is in the correct range: Article accepted")

        # Define keyword sets with singular, plural, and title case forms
        conference_keywords = {
            'conference', 'conferences', 'proceeding', 'proceedings',
            'workshop', 'workshops', 'meeting', 'meetings',
            'Conference', 'Conferences', 'Proceeding', 'Proceedings',
            'Workshop', 'Workshops', 'Meeting', 'Meetings'
        }

        ignored_keywords = {
            'publication date', 'publication dates', 'authors', 'author',
            'descriptions', 'description', 'scholar articles', 'publisher',
            'publishers', 'volume', 'volumes', 'page', 'pages', 'issue', 'issues'
            'Publication Date', 'Publication Dates', 'Authors', 'Author',
            'Descriptions', 'Description', 'Scholar Articles', 'Publisher',
            'Publishers', 'Volume', 'Volumes', 'Page', 'Pages', 'Issue', 'Issues'
        }

        citations_keywords = {
            'total citations', 'total citation',
            'Total Citations', 'Total Citation'
        }

        preprint_keywords = {
            'preprint', 'preprints', 'arxiv', 'biorxiv', 'medrxiv',
            'Preprint', 'Preprints', 'Arxiv', 'Biorxiv', 'Medrxiv'
        }

        journal_keywords = {
            'journal', 'journals',
            'Journal', 'Journals'
        }

        book_keywords = {
            'book', 'books',
            'Book', 'Books'
        }

        patent_keywords = {
            'patent', 'patents',
            'Patent', 'Patents'
        }

        old_counters = counters.copy()

        for field, value in zip(fields, values):
            article_field = field.string.lower().strip()

            if any(keyword in article_field for keyword in citations_keywords):
                if value:
                    match = re.search(r'Cited by (\d+)', str(value))
                    if match:
                        cited_by_number = match.group(1)
                        counters['Citation Count'] += int(cited_by_number)
                        print("Checkpoint 12: 'Cited by' number found: Good")
                    else:
                        print("Checkpoint 12: No 'Cited by' number found: Bad\nProblematic URL: \"{url}\"")

            if value and any(keyword in str(value) for keyword in preprint_keywords):
                counters['arXiv Preprint'] += 1
                continue

            # Handle journal-related keywords
            if any(keyword in article_field for keyword in journal_keywords) and 'preprint' not in str(value):
                counters['Peer Reviewed Articles'] += 1
                continue

            # Handle conference-related keywords
            if any(keyword in article_field for keyword in conference_keywords) or (value and any(keyword in str(value) for keyword in conference_keywords)):
                counters['Conference Papers'] += 1
                continue

            if any(keyword in article_field for keyword in book_keywords):
                counters['Books'] += 1

                # Check if the next field is 'book chapter' and has pages
                next_field_index = fields.index(field) + 1
                if next_field_index < len(fields):
                    next_article_field = fields[next_field_index].string.lower(
                    ).strip()
                    next_value = values[next_field_index]

                    if 'book chapter' in next_article_field and str(next_value):
                        counters['Book Chapters'] += 1
                        counters['Books'] -= 1
                continue

            if any(keyword in article_field for keyword in patent_keywords):
                counters['Patent'] += 1
                continue

            # Check for ignored fields
            if any(ignored_keyword in article_field for ignored_keyword in ignored_keywords):
                continue

            # Handle cases that don't match any known keyword
            if not (any(keyword in article_field for keyword in (citations_keywords | preprint_keywords | journal_keywords | conference_keywords | book_keywords | patent_keywords)) or
                    any(keyword in str(value) for keyword in (conference_keywords | preprint_keywords))):
                print(
                    f"\nMANUAL INSPECTION REQUIRED:\n{url}\nUnknown article_field: {article_field}.")

        if counters == old_counters:
            print(f"\nMANUAL INSPECTION REQUIRED:\n{url}\nNo counts updated.")
        else:
            print("UPDATED VALUES: ", counters, "\n")

        print(f"Checkpoint 7: Article was scraped successfully: Good")
        return counters, True

    except requests.RequestException as e:
        print(f"Checkpoint 7: Error fetching data from article: Bad\nProblematic URL: \"{e}\"")
        return counters


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
                    profile_data.get('Total Citations', '')
                ])


input_file = 'test_url.txt'  # File containing list of URLs
output_file = 'output.csv'  # File to save the results
input_year = 2023  # Year to extract (ex. put 2023 for May 2023 - April 2024)

# Run the process
process_urls(input_file, output_file)
