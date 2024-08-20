from bs4 import BeautifulSoup
import requests
import csv
import time
import random
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re


def transform_url(original_url):
    """Transform the given URL to the desired format."""
    if not original_url:
        print(f"Checkpoint 1: URL empty.")
        return None
    else:
        print(f"Checkpoint 1: Good")

    # Ensure the URL has a scheme
    if not original_url.startswith(('http://', 'https://')):
        print(f"Checkpoint 2: Invalid URL scheme: {original_url}")
        return None
    else:
        print(f"Checkpoint 2: Good")

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
        print(f"Checkpoint 3: No data for {url} found.")
        return None

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
        profile_data['Full Name'] = name.string if name else "Unknown"

        # Extract h-index values
        h_index = doc.find_all(string="h-index")
        if h_index:
            parent = h_index[0].parent.parent.parent
            td_elements = parent.find_all('td')
            profile_data['H-Index Overall'] = td_elements[-2].get_text(
                strip=True)
            profile_data['H-Index Since'] = td_elements[-1].get_text(
                strip=True)
        else:
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

        # Process each article URL
        for article_url in article_urls:
            time.sleep(2)  # Rate limit
            print(counters, "\n\n")
            counters = scrape_article(article_url, counters)
            print(counters, "\n\n")

        # Add total citations to profile data
        profile_data['Total Citations'] = counters['Citation Count']

        # Add the counters to the profile data
        for key, value in counters.items():
            profile_data[key] = value

        return profile_data

    except requests.RequestException as e:
        print(f"Checkpoint 4: Error fetching data from URL: {e}")
        return None


def scrape_article(url, counters):
    """Function to scrape an article"""

    if not url:
        print(f"Checkpoint 7: No data for {url} found.")
        return counters

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

        if date and date.count('/') == 2:
            year, month, day = date.split('/')
            year = int(year)
            month = int(month)
        else:
            return counters

        if not (year == input_year and month >= 5 or year == input_year + 1 and month < 5):
            return counters

        for field, value in zip(fields, values):
            articleField = field.string.lower().strip()

            if articleField == 'total citations' and value.string:
                match = re.search(r'Cited by (\d+)', value.string)
                if match:
                    cited_by_number = match.group(1)
                    counters['Citation Count'] += int(cited_by_number)

            elif 'preprint' in value:
                counters['arXiv Preprint'] += 1

            elif articleField == 'journal' and 'preprint' not in value:
                counters['Peer Reviewed Articles'] += 1

            elif 'conference' in articleField:
                counters['Conference Papers'] += 1

            elif articleField == 'book':
                counters['Books'] += 1

            elif articleField == 'book chapter':
                counters['Book Chapters'] += 1

            elif 'patent' in articleField:
                counters['Patent'] += 1

        return counters

    except requests.RequestException as e:
        print(f"Checkpoint 8: Error fetching data from URL: {e}")
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
            'Total Citations'
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

