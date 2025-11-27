import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import argparse

URL = "https://realpython.github.io/fake-jobs/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def parse_args() -> argparse.Namespace:
    """Parst die Kommandozeilenargumente."""
    parser = argparse.ArgumentParser(
        description="Scrapt eine Demo-Jobseite und filtert nach einem Suchwort im Jobtitel."
    )
    parser.add_argument(
        "-k",
        "--keyword",
        type=str,
        required=True,
        help="Suchwort, das im Jobtitel enthalten sein soll (z.B. 'python', 'engineer').",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Optionaler Dateiname für die Ausgabedatei (CSV). Wenn nicht gesetzt, wird aus dem Keyword ein Name erzeugt.",
    )
    return parser.parse_args()


def fetch_page(url: str) -> str:
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.text


def parse_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find(id="ResultsContainer")

    if results is None:
        print("Konnte den Ergebnis-Container nicht finden.")
        return []

    job_cards = results.find_all("div", class_="card-content")

    jobs = []
    for job in job_cards:
        title_tag = job.find("h2")
        company_tag = job.find("h3")
        location_tag = job.find("p", class_="location")
        link_tag = job.find("a", string="Apply")

        jobs.append(
            {
                "title": title_tag.get_text(strip=True) if title_tag else "N/A",
                "company": company_tag.get_text(strip=True) if company_tag else "N/A",
                "location": location_tag.get_text(strip=True) if location_tag else "N/A",
                "link": link_tag["href"] if link_tag else "N/A",
            }
        )

    return jobs


def filter_jobs_by_keyword(jobs: list[dict], keyword: str) -> list[dict]:
    keyword = keyword.lower()
    return [job for job in jobs if keyword in job["title"].lower()]


def build_filename_from_keyword(keyword: str) -> str:
    safe_keyword = re.sub(r"[^a-zA-Z0-9_-]+", "_", keyword.lower())
    return f"{safe_keyword}_jobs.csv"


def save_jobs_to_csv(jobs: list[dict], filename: str) -> None:
    if not jobs:
        print("Es wurden keine Jobs zum Speichern übergeben.")
        return

    df = pd.DataFrame(jobs)
    df.rename(
        columns={
            "title": "Jobtitel",
            "company": "Firma",
            "location": "Ort",
            "link": "Link",
        },
        inplace=True,
    )
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"{len(df)} Jobs gespeichert in '{filename}'.")


def main() -> None:
    args = parse_args()
    keyword = args.keyword.strip()
    if not keyword:
        print("Leeres Keyword übergeben. Beende Script.")
        return

    html = fetch_page(URL)
    jobs = parse_jobs(html)

    if not jobs:
        print("Keine Jobs gefunden oder Seite konnte nicht geparst werden.")
        return

    filtered_jobs = filter_jobs_by_keyword(jobs, keyword)

    if not filtered_jobs:
        print(f"Keine Jobs gefunden, die '{keyword}' im Titel enthalten.")
        return

    if args.output:
        filename = args.output
    else:
        filename = build_filename_from_keyword(keyword)

    save_jobs_to_csv(filtered_jobs, filename)


if __name__ == "__main__":
    main()
