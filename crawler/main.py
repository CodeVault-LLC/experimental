import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def find_text_files(seed_url, max_links=50):
    """
    Recursively crawls a website starting from the seed URL to find .txt files.

    :param seed_url: The starting URL for the crawler.
    :param max_links: Maximum number of .txt file links to find.
    :return: List of found .txt file URLs.
    """
    visited = set()
    txt_links = []
    urls_to_visit = [seed_url]

    while urls_to_visit and len(txt_links) < max_links:
        current_url = urls_to_visit.pop(0)

        if current_url in visited:
            continue

        try:
            print(f"Visiting: {current_url}")
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()

            visited.add(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links on the current page
            for a_tag in soup.find_all('a', href=True):
                link = urljoin(current_url, a_tag['href'])
                if link not in visited and link not in urls_to_visit:
                    if link.endswith('.txt'):
                        txt_links.append(link)
                        print(f"Found text file: {link}")
                        if len(txt_links) >= max_links:
                            break
                    elif link.startswith(seed_url):
                        urls_to_visit.append(link)

        except requests.RequestException as e:
            print(f"Failed to fetch {current_url}: {e}")

    return txt_links

if __name__ == "__main__":
    seed_url = "https://wa.me"  # Replace with the starting URL
    max_results = 50
    print("Starting crawler...")
    text_files = find_text_files(seed_url, max_results)
    print("\nFinished crawling. Found .txt files:")
    for idx, file_url in enumerate(text_files, start=1):
        print(f"{idx}: {file_url}")
