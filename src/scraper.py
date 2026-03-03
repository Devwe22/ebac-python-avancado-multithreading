
import requests
import time
import csv
import random
import concurrent.futures
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "pt-BR,pt;q=0.9"
}

BASE_URL = "https://www.imdb.com"
POPULAR_URL = f"{BASE_URL}/chart/moviemeter/"
MAX_THREADS = 10


def extract_movie_details(movie_url):
    try:
        time.sleep(random.uniform(0.1, 0.3))
        response = requests.get(movie_url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, "html.parser")

        title = soup.find("span", {"data-testid": "hero__primary-text"})
        title = title.get_text(strip=True) if title else "N/A"

        rating = soup.find("span", {"class": "sc-bde20123-1"})
        rating = rating.get_text(strip=True) if rating else "N/A"

        return [title, rating]

    except Exception:
        return None


def main():
    response = requests.get(POPULAR_URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")

    movie_tags = soup.find_all("a", {"class": "ipc-title-link-wrapper"})
    movie_links = [BASE_URL + tag["href"].split("?")[0] for tag in movie_tags[:20]]

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(extract_movie_details, url) for url in movie_links]

        for future in concurrent.futures.as_completed(futures):
            data = future.result()
            if data:
                results.append(data)

    with open("movies.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Rating"])
        writer.writerows(results)


if __name__ == "__main__":
    main()
