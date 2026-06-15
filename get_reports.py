"""
Parker Jackson
May 2025
Reading Bucknell Public Safety Reports
Main execution file
"""

import argparse
import concurrent.futures
import html
import io
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

import requests
import urllib3


# disable warnings from unverified website
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL headers
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
}

REPORTS_DIR = "reports"
NEW_FORMAT_START = datetime(2025, 6, 1).date()
NEW_FORMAT_BASE_URL = "https://www.bucknell.edu/82c8b9cd-d792-4d3e-b2ed-bb4f05c662c7-{}"

ARTICLE_RE = re.compile(
    r"<article\b[^>]*node--type-crime-log[^>]*>(.*?)</article>",
    re.IGNORECASE | re.DOTALL,
)
DATETIME_RE = re.compile(r"<time\b[^>]*datetime=\"([^\"]+)\"", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
DATE_LINE_RE = re.compile(r"^[A-Z][a-z]{2}, \d{2}/\d{2}/\d{4} - \d{2}:\d{2}$")


def get_text(file):
    """Gets the text from a given PDF file."""
    text = ""
    for page in file:
        text += page.get_text()
    return text


def get_file(url):
    """Return the PDF file from a given URL."""
    import fitz

    response = requests.get(url=url, headers=HEADERS, verify=False, timeout=30)
    if response.status_code != 200:
        raise Exception(f"Failed to download the PDF from {url}")

    return fitz.open(stream=io.BytesIO(response.content), filetype="pdf")


def create_prompt(text, date):
    prompt = f"""
    You are a data assistant. Extract the crime log data from the following text and return it as a Python array of objects.
    Each object must have keys: Date ({date.strftime('%m/%d/%Y')}), Time, Location, Nature, Case Number, and Disposition. Disregard entry if the date listed does not match the date provided.
    Return ONLY the JSON array. Do NOT include markdown code fences (```), explanations, or extra text.
    Raw text:
    {text}
    """
    return prompt


def output_path(report_date):
    return os.path.join(REPORTS_DIR, f"crime_log_{report_date.isoformat()}.json")


def save_report(report_date, entries):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(output_path(report_date), "w") as json_file:
        json.dump(entries, json_file, indent=4)


def clean_article_lines(article_html):
    text = TAG_RE.sub("\n", article_html)
    lines = []
    for line in html.unescape(text).splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()
        if cleaned:
            lines.append(cleaned)
    return lines


def parse_new_format_page(index, page_html):
    article_match = ARTICLE_RE.search(page_html)
    if not article_match:
        return None

    datetime_match = DATETIME_RE.search(article_match.group(1))
    if not datetime_match:
        return None

    report_date = datetime.fromisoformat(
        datetime_match.group(1).replace("Z", "+00:00")
    ).date()
    if report_date < NEW_FORMAT_START:
        return None

    lines = [
        line
        for line in clean_article_lines(article_match.group(1))
        if not DATE_LINE_RE.match(line)
    ]

    if not lines or any(line.lower() == "no crime to report." for line in lines):
        return index, report_date, []

    entry = {
        "Date": report_date.strftime("%m/%d/%Y"),
        "Time": "",
        "Location": lines[2] if len(lines) > 2 else "",
        "Nature": lines[0] if len(lines) > 0 else "",
        "Case Number": lines[1] if len(lines) > 1 else "",
        "Disposition": lines[3] if len(lines) > 3 else "",
    }
    return index, report_date, [entry]


def fetch_new_format_page(index):
    url = NEW_FORMAT_BASE_URL.format(index)
    try:
        response = requests.get(url=url, headers=HEADERS, timeout=30)
    except requests.RequestException as exc:
        print(f"Warning: Failed to request {url}: {exc}")
        return index, None

    if response.status_code not in (200, 403):
        return index, None

    parsed = parse_new_format_page(index, response.text)
    return index, parsed


def discover_new_format_reports(start_index=1, max_empty=40, workers=12):
    reports_by_date = defaultdict(list)
    seen_dates = set()
    highest_index = 0
    empty_streak = 0
    index = start_index

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        while True:
            batch = list(range(index, index + workers))
            results = list(executor.map(fetch_new_format_page, batch))

            for page_index, parsed in sorted(results):
                if parsed is None:
                    if highest_index:
                        empty_streak += 1
                    continue

                empty_streak = 0
                source_index, report_date, entries = parsed
                highest_index = max(highest_index, source_index)
                seen_dates.add(report_date)
                reports_by_date[report_date].extend(entries)

            if highest_index and empty_streak >= max_empty:
                break

            index += workers

    return reports_by_date, seen_dates, highest_index


def refresh_new_format_reports(start_index=1, max_empty=40, workers=12):
    reports_by_date, seen_dates, highest_index = discover_new_format_reports(
        start_index=start_index,
        max_empty=max_empty,
        workers=workers,
    )

    if not seen_dates:
        print("No new-format crime-log pages found.")
        return

    latest_date = max(seen_dates)
    current_date = NEW_FORMAT_START
    written = 0

    while current_date <= latest_date:
        entries = reports_by_date.get(current_date, [])
        save_report(current_date, entries)
        written += 1
        current_date += timedelta(days=1)

    total_entries = sum(len(entries) for entries in reports_by_date.values())
    print(
        f"Updated {written} report files from {NEW_FORMAT_START.isoformat()} "
        f"through {latest_date.isoformat()} using new-format indices through "
        f"{highest_index}; parsed {total_entries} incident entries."
    )


def get_openai_client():
    from openai import OpenAI

    return OpenAI()


def refresh_legacy_pdf_reports(days=3):
    """Fetch recent pre-June-2025 PDFs. Kept for historical URL support."""
    client = get_openai_client()
    two_days_ago = datetime.now() - timedelta(days=1)

    for i in range(days):
        current_date = two_days_ago - timedelta(days=i)
        if current_date.date() >= NEW_FORMAT_START:
            continue

        date_str = current_date.strftime("%m%d%y")
        urls = [
            f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2E2%2Epdf",
            f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2E1%2Epdf",
        ]

        combined_text = ""
        for url in urls:
            try:
                pdf_file = get_file(url)
                combined_text += get_text(pdf_file)
            except Exception as e:
                print(f"Warning: Failed to download or read PDF from {url}: {e}")

        report_date = current_date.date()
        if not combined_text:
            print(f"No PDFs available for {report_date.isoformat()}, saving empty report.")
            save_report(report_date, [])
            continue

        prompt = create_prompt(combined_text, current_date)
        response = client.responses.create(model="gpt-4.1", input=prompt)

        entries_str = response.output_text
        try:
            entries = json.loads(entries_str)
        except json.JSONDecodeError as e:
            print("Failed to parse JSON from OpenAI response:")
            print(f"Error: {e}")
            print(f"Response content was:\n{entries_str}")
            break

        save_report(report_date, entries)


def main():
    parser = argparse.ArgumentParser(description="Update Bucknell Public Safety reports.")
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--max-empty", type=int, default=40)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument(
        "--legacy-days",
        type=int,
        default=0,
        help="Also update this many recent pre-June-2025 PDF reports.",
    )
    args = parser.parse_args()

    refresh_new_format_reports(
        start_index=args.start_index,
        max_empty=args.max_empty,
        workers=args.workers,
    )

    if args.legacy_days:
        refresh_legacy_pdf_reports(days=args.legacy_days)


if __name__ == "__main__":
    main()
