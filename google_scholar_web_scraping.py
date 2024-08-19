from bs4 import BeautifulSoup
import requests
import csv
import time


def get_updated_url(old_url):
    try:
        response = requests.get(old_url)
        response.raise_for_status()  # Check if the request was successful

        soup = BeautifulSoup(response.content, 'html.parser')

        # Example: Adjust according to the actual page structure
        new_url_element = soup.find('a', {'id': 'updated-profile-link'})
        if new_url_element:
            return new_url_element['href']
        else:
            return old_url  # Return the old URL if no new URL is found
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return old_url  # Return the old URL if there is an error

# Function to scrape data from a URL


def scrape_data(url):
    # Ensure URL is valid
    if not url:
        return None, None, None, None

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        result = requests.get(url, headers=headers)
        result.raise_for_status()  # Check if the request was successful
        doc = BeautifulSoup(result.text, 'html.parser')

        # Find the name of the google scholar
        name = doc.find(id="gsc_prf_i")
        if name:
            name = name.get_text(strip=True)  # Extract and clean text
        else:
            name = "Unknown"

        # Find where h_index is located
        h_index = doc.find_all(string="h-index")
        if h_index:
            parent = h_index[0].parent.parent.parent
            td_elements = parent.find_all('td')

            # Extract the h_index values
            h_index_all = td_elements[-2].get_text(strip=True)
            h_index_since_year = td_elements[-1].get_text(strip=True)
        else:
            h_index_all = h_index_since_year = None

        # Extract years and values
        years = [span.get_text(strip=True)
                 for span in doc.find_all('span', class_='gsc_g_t')]
        values = [a.find('span', class_='gsc_g_al').get_text(strip=True)
                  for a in doc.find_all('a', class_='gsc_g_a')]

        # Find the value of the year
        year_index = years.index(str(year)) if str(year) in years else None
        year_value = values[year_index] if year_index is not None and year_index < len(
            values) else None

        return name, h_index_all, h_index_since_year, year_value
    except requests.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        return None, None, None, None

# Function to process a list of URLs


def process_urls(input_file, output_file):
    since_year = year - 4

    # Read the URLs and create a CSV file
    with open(input_file, 'r') as file:
        urls = file.read().splitlines()

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Full Name', 'Link', 'Google Scholar',
            f'Citation Count {year}',
            f'H-Index Since {since_year}', 'H-Index Overall',
            f'Peer Reviewed Articles {year}',
            f'arXiv Preprint {year}',
            f'Books {year}',
            f'Book Chapters {year}',
            f'Conference Papers {year}',
            f'Patent {year}',
            'Total Citations',
            f'Average Citations per Researcher in {year}',
            f'Average H-Index Since {since_year} per Researcher',
            'Average Overall H-Index',
            'Total Peer Reviewed Articles',
            'Average Peer Reviewed Publications per Researcher',
            'Total Conference Papers'
        ])

        # Process each URL
        for url in urls:
            url = get_updated_url(url)

            # Rate limit to avoid hitting the server too quickly
            time.sleep(2)  # Sleep for 2 seconds between requests

            name, h_index_since_year, h_index_all, year_value = scrape_data(
                url)
            google_scholar = "Yes"

            writer.writerow([name, url, google_scholar, year_value,
                            h_index_since_year, h_index_all, '', '', '', '', '', '', '', '', '', '', '', '', ''])


input_file = 'test_url.txt'  # File containing list of URLs
output_file = 'output.csv'  # File to save the results
year = 2023  # Year to extract start of (ex. put 2023 for May 2023-April 2024)

# Run the process
process_urls(input_file, output_file)
