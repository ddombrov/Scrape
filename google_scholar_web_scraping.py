from bs4 import BeautifulSoup
import requests
import csv
import time
import random


def get_updated_url(url):
    """Function to get the updated URL"""

    return url

    # UPDATE THIS LATER
    # try:

    #     # Send a GET request to the URL
    #     # Check if the request was successful
    #     # Parse the HTML content of the page
    #     response = requests.get(old_url)
    #     response.raise_for_status()
    #     doc = BeautifulSoup(response.content, 'html.parser')

    #     new_url_element = doc.find('a', {'id': 'updated-profile-link'})
    #     if new_url_element:
    #         return new_url_element['href']
    #     else:
    #         return old_url

    # except requests.RequestException as e:
    #     print(f"Error fetching the URL: {e}")
    #     return old_url


def scrape_data(url):
    """Function to scrape data from a URL"""

    # Check if the URL is empty
    if not url:
        return None, None, None, None, None, None, None, None, None

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
        name = doc.find(id="gsc_prf_i")
        if name:
            name = name.get_text(strip=True)
        else:
            name = "Unknown"

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

        # Click on gsc_a_ha with value Year (this will sort list by years descending)
        # Find the tbody with id gsc_a_b this is like array of articles
        # articles have gsc_a_tr, then subclass gsc_a_t then that has the link
        # in a loop add all links of articles to article_urls
        # if article 20 has a valid date then you have to click the button with id gs_wr and text Show more to load more articles and keep loop going

        article_urls = []

        # Process each article
        for article_url in article_urls:

            # Rate limit to avoid hitting the server too quickly
            time.sleep(2)

            # Scrape the data from the URL
            citation_count, peer_reviewed, books, book_chapters, conference_papers, patents = scrape_article(
                article_url)

        return name, citation_count, h_index_since_input_year, h_index_all, peer_reviewed, books, book_chapters, conference_papers, patents
    except requests.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        return None, None, None, None, None, None, None, None, None


def scrape_article(url):
    """Function to scrape an article URL"""

    # Check if the URL is empty
    if not url:
        return None, None, None, None, None, None

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

        # Find the date of the artcle
        date = doc.find(id="gsc_oci_value")
        year, month = date.split('/')

        # Check if the article is within the specified year
        if not (year == input_year and month >= 5 or year == input_year+1 and month < 5):
            return None

        prePrint = 0
        conference = 0
        journal = 0
        book = 0
        bookChapter = 0
        patents = 0

        # Extract and process the article types
        fields = doc.find_all('div', class_='gsc_oci_field')
        values = doc.find_all('div', class_='gsc_oci_value')

        # Iterate over fields and values
        for field, value in zip(fields, values):

            # Get the text and convert to lowercase
            articleType = field.get_text(strip=True).lower()

            # Increment counters based on article type
            if articleType == 'preprint':
                prePrint += 1
            elif articleType == 'conference':
                conference += 1
            elif articleType == 'journal':
                journal += 1
            elif articleType == 'book':
                book += 1
            elif articleType == 'book chapter':
                bookChapter += 1
            elif articleType == 'patents':
                patents += 1

        return prePrint, conference, journal, book, bookChapter, patents

    except requests.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        return None, None, None, None, None, None


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
            url = get_updated_url(url)

            # Rate limit to avoid hitting the server too quickly
            time.sleep(random.uniform(1, 3))

            # Scrape the data from the URL
            name, citation_count, h_index_since_input_year, h_index_all, peer_reviewed, books, book_chapters, conference_papers, patents = scrape_data(
                url)

            # Write the data to the CSV file
            writer.writerow([name, url, "Yes", citation_count, h_index_since_input_year,
                            h_index_all, peer_reviewed, books, book_chapters, conference_papers, patents])


input_file = 'test_url.txt'  # File containing list of URLs
output_file = 'output.csv'  # File to save the results
input_year = 2023  # Year to extract (ex. put 2023 for May 2023 - April 2024)

# Run the process
process_urls(input_file, output_file)
