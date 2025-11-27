import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://quotes.toscrape.com/page/{}/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_page(page_number: int) -> str | None:
    """Lädt eine Seite mit Quotes. Gibt None zurück, wenn Seite nicht existiert."""
    url = BASE_URL.format(page_number)
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 404:
        # Seite existiert nicht (mehr)
        return None

    response.raise_for_status()
    return response.text


def parse_quotes(html: str) -> list[dict]:
    """Parst alle Zitate auf einer Seite und gibt sie als Liste von Dicts zurück."""
    soup = BeautifulSoup(html, "html.parser")
    quote_elements = soup.find_all("div", class_="quote")

    quotes = []
    for q in quote_elements:
        text_tag = q.find("span", class_="text")
        author_tag = q.find("small", class_="author")
        tag_elements = q.find_all("a", class_="tag")

        text = text_tag.get_text(strip=True) if text_tag else "N/A"
        author = author_tag.get_text(strip=True) if author_tag else "N/A"
        tags = [t.get_text(strip=True) for t in tag_elements]

        quotes.append(
            {
                "text": text,
                "author": author,
                "tags": ", ".join(tags),
            }
        )

    return quotes


def scrape_all_quotes(max_pages: int = 10) -> list[dict]:
    """Scraped mehrere Seiten, bis keine Quotes mehr gefunden werden."""
    all_quotes = []

    for page in range(1, max_pages + 1):
        print(f"Scrape Seite {page}...")
        html = fetch_page(page)
        if html is None:
            print(f"Seite {page} existiert nicht. Stoppe.")
            break

        quotes = parse_quotes(html)
        if not quotes:
            print(f"Keine Zitate auf Seite {page} gefunden. Stoppe.")
            break

        all_quotes.extend(quotes)

    return all_quotes


def save_quotes_to_csv(quotes: list[dict], filename: str = "quotes.csv") -> None:
    df = pd.DataFrame(quotes)
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"{len(df)} Zitate in '{filename}' gespeichert.")


def main() -> None:
    quotes = scrape_all_quotes(max_pages=10)
    if not quotes:
        print("Es wurden keine Zitate gefunden.")
        return

    save_quotes_to_csv(quotes)


if __name__ == "__main__":
    main()
