"""
Parker Jackson
Nov 2024
Reading Bucknell Public Safety Reports
Main execution file
"""

import io
import requests
from datetime import datetime, timedelta
from PyPDF2 import PdfReader
from crime_date import CrimeDate, Incident
import urllib3

# disable warnings from unverified website
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}

""" Gets the text from a given file, handling one or multiple pages """
def get_text(file):
    text = ""  # Initialize an empty string to hold all pages' text

    if file.pages == 1:
        # Only 1 page
        text = file[0].extract_text()

    else:
        # Multiple pages, loop through each page and append the text
        for page_num in range(len(file.pages)):
            page = file.pages[page_num]
            text += page.extract_text()  # Append text from each page

    return text

""" Return the PDF file from a given URL """
def get_file(url):
    response1 = requests.get(url=url, headers=HEADERS, timeout=120, verify=False)
    on_fly_mem_obj1 = io.BytesIO(response1.content)
    pdf_file1 = PdfReader(on_fly_mem_obj1)

    return pdf_file1


""" Get data from past 30 days and print out."""
def main():
    # Get data from last 30 days, starting 2 days ago (PDFs always start 2 days previous)

    # Calculate the date two days ago
    two_days_ago = datetime.now() - timedelta(days=2)
    days = 30
    day_reports = []

    for i in range(days):
        # get the date string
        current_date = two_days_ago - timedelta(days=i)
        date_str = current_date.strftime('%m%d%y')

        url1 = f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2E2%2Epdf"
        url2 = f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2E1%2Epdf"

        # get files from URL
        pdf_file1 = get_file(url1)
        pdf_file2 = get_file(url2)

        # read file texts
        text1 = get_text(pdf_file1)
        text2 = get_text(pdf_file2)

        # Read entry data
        split_text = text1.splitlines()

        crimedate = CrimeDate(split_text[3])

        if split_text[4] == "-":
            print("no reports")
            day_reports.append(crimedate)
            continue

        for i, line in enumerate(split_text):
            # Get Date
            if i == 3:
                crimedate = CrimeDate(line)

            # Check for no reports
            elif i == 4:
                if line == "-":
                    # No reports
                    print("No reports")
                    break

            # Check number of offenses
            

        day_reports.append(crimedate)
        # break

main()
