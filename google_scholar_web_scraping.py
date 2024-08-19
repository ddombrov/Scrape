from bs4 import BeautifulSoup
import requests
import csv
import time
import random
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def transform_url(original_url):
    """Transform the given URL to the desired format."""
    if not original_url:
        return None

    # Ensure the URL has a scheme
    if not original_url.startswith(('http://', 'https://')):
        print(f"Invalid URL scheme: {original_url}")
        return None

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
        print(f"No data for {url} found.")
        return None, None, None, None, None, None, None, None, None, None

    # Set the headers for the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Send a GET request to the URL
        # Check if the request was successful
        # Parse the HTML content of the page
        result = requests.get(url, headers=headers)
        result.raise_for_status()
        doc = BeautifulSoup(result.text, 'html.parser')

        # Find the name of the google scholar
        name = doc.find(id="gsc_prf_in")
        if name:
            name = name.string
        else:
            name = "Unknown"
            print(f"No data for {url} found: Name not found.")

        # Find where h_index values are located
        # Extract the h_index values
        h_index = doc.find_all(string="h-index")
        if h_index:
            parent = h_index[0].parent.parent.parent
            td_elements = parent.find_all('td')
            h_index_all = td_elements[-2].get_text(strip=True)
            h_index_since_input_year = td_elements[-1].get_text(strip=True)
        else:
            h_index_all = h_index_since_input_year = None
            print(f"No data for {url} found: H-Index values not found.")

        article_urls = []
        base_url = 'https://scholar.google.ca'

        # link_location = doc.find_all(id="gsc_a_b").find_all(id="gsc_a_tr").find_all(id="gsc_a_t")
        # for link in link_location:

        #     articles = link.find_all('a', href=True)
        #     for article in articles:
        #         href = article['href']
        #         if href.startswith('/'):
        #             href = base_url + href
        #         # Add the URL to the list if it is not empty
        #         if href:
        #             article_urls.append(href)

        # Find the parent element
        parent_element = doc.find(id='gsc_a_b')

        if parent_element:
            # Iterate over all children with id 'gsc_a_tr'
            children = parent_element.find_all(id='gsc_a_tr')

            for child in children:
                # Find all grandchildren with id 'gsc_a_t' within each child
                grandchildren = child.find_all(id='gsc_a_t')

                for grandchild in grandchildren:
                    # Find all links within the grandchild
                    articles = grandchild.find_all('a', href=True)
                    print("\n\n", articles)

                    for article in articles:
                        href = article['href']
                        if href.startswith('/'):
                            href = base_url + href
                        # Add the URL to the list if it is not empty
                        if href:
                            article_urls.append(href)

        # print(article_urls)
        # article_urls.append(
        #     "https://scholar.google.ca/citations?view_op=view_citation&hl=en&user=WUlj9lsAAAAJ&sortby=pubdate&citation_for_view=WUlj9lsAAAAJ:uLbwQdceFCQC")

        # Scrape the data from the URL
        citation_count = 0
        peer_reviewed = 0
        preprint = 0
        books = 0
        book_chapters = 0
        conference_papers = 0
        patents = 0

        # Process each article
        for article_url in article_urls:

            # Rate limit to avoid hitting the server too quickly
            time.sleep(2)

            citation_count, peer_reviewed, preprint, books, book_chapters, conference_papers, patents = scrape_article(
                article_url)

        return name, citation_count, h_index_since_input_year, h_index_all, peer_reviewed, preprint, books, book_chapters, conference_papers, patents
    except requests.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        return None, None, None, None, None, None, None, None, None, None


def scrape_article(url):
    """Function to scrape an article"""

    # Check if the URL is empty
    if not url:
        print(f"No data for {url} found.")
        return None, None, None, None, None, None, None

    # Set the headers for the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:

        # Send a GET request to the URL
        # Check if the request was successful
        # Parse the HTML content of the page
        result = requests.get(url, headers=headers)
        result.raise_for_status()
        doc = BeautifulSoup(result.text, 'html.parser')

        # Extract and process the article types
        fields = doc.find_all('div', class_='gsc_oci_field')
        values = doc.find_all('div', class_='gsc_oci_value')

        date = None

        for field, value in zip(fields, values):
            if field.string and 'publication date' in field.string.strip().lower():
                date = value.string.strip() if value.string else value.get_text(strip=True)
                break
        if date is not None and date.count('/') == 2:
            year, month, day = date.split('/')
        else:
            print(f"\n\nNo data for {url} found: Publication date not found.")
            return None, None, None, None, None, None, None

        year = int(year)
        month = int(month)

        # Check if the article is within the specified year
        if not (year == input_year and month >= 5 or year == input_year+1 and month < 5):
            return None, None, None, None, None, None, None

        citation_count = 0
        peer_reviewed = 0
        preprint = 0
        books = 0
        book_chapters = 0
        conference_papers = 0
        patents = 0

        # Iterate over fields and values
        for field, value in zip(fields, values):

            # Get the text and convert to lowercase
            articleType = field.string.lower()

            if articleType == 'total citations':
                # count=value.string
                count = 0
                # citation_count+=

            # Increment counters based on article type (can be multiple but not preprint and journal)
            if articleType == 'preprint':
                preprint += 1
                # print(articleType, preprint)

            elif articleType == 'journal':
                peer_reviewed += 1
                # print("\n\n", articleType, peer_reviewed, "\n\n")

            if articleType == 'conference':
                conference_papers += 1
                # print(articleType, conference_papers)

            if articleType == 'book':
                books += 1
                # print(articleType, books)

            if articleType == 'book chapter' or articleType == 'pages':
                book_chapters += 1
                # print(articleType, book_chapters)

            if articleType == 'patent' or articleType == 'patent office':
                patents += 1
                # print(articleType, patents)

        return citation_count, peer_reviewed, preprint, books, book_chapters, conference_papers, patents

    except requests.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        return None, None, None, None, None, None, None


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

            # Get the updated URL
            # url = get_updated_url(url)

            # Rate limit to avoid hitting the server too quickly
            time.sleep(random.uniform(1, 3))

            # Scrape the data from the URL
            name, citation_count, h_index_since_input_year, h_index_all, peer_reviewed, preprint, books, book_chapters, conference_papers, patents = scrape_profile(
                url)

            # Write the data to the CSV file
            writer.writerow([name, url, "Yes", citation_count, h_index_since_input_year,
                            h_index_all, peer_reviewed, preprint, books, book_chapters, conference_papers, patents])


input_file = 'test_url.txt'  # File containing list of URLs
output_file = 'output.csv'  # File to save the results
input_year = 2023  # Year to extract (ex. put 2023 for May 2023 - April 2024)

# Run the process
process_urls(input_file, output_file)
# scrape_article('https://scholar.google.ca/citations?view_op=view_citation&hl=en&user=WUlj9lsAAAAJ&sortby=pubdate&citation_for_view=WUlj9lsAAAAJ:7T2F9Uy0os0C')
