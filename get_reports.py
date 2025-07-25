"""
Parker Jackson
May 2025
Reading Bucknell Public Safety Reports
Main execution file
"""

import io
import json
import requests
from datetime import datetime, timedelta
import fitz
import urllib3
from openai import OpenAI
import os

# disable warnings from unverified website
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL headers
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}

# Initialize OpenAI API
client = OpenAI()

def get_text(file):
    """ Gets the text from a given file """
    text = ""  # Initialize an empty string to hold all pages' text

    for page in file:
        text += page.get_text()

    return text

def get_file(url):
    """ Return the PDF file from a given URL """

    # request pdf from the URL
    response = requests.get(url=url, headers=HEADERS, verify=False)
    if response.status_code != 200:
        raise Exception(f"Failed to download the PDF from {url}")
    
    pdf_file = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")

    return pdf_file

def create_prompt(text, date):
    prompt = f"""
    You are a data assistant. Extract the crime log data from the following text and return it as a Python array of objects.
    Each object must have keys: Date ({date.strftime('%m/%d/%Y')}), Time, Location, Nature, Case Number, and Disposition. Disregard entry if the date listed does not match the date provided.
    Return ONLY the JSON array. Do NOT include markdown code fences (```), explanations, or extra text.
    Raw text:
    {text}
    """
    return prompt


def main():
    """ Get data from past 30 days and print out """
    # Get data from last 30 days, starting 2 days ago (PDFs always start 2 days previous)

    # Calculate the date two days ago
    two_days_ago = datetime.now() - timedelta(days=1)
    days = 3
    all_entries = []
    
    for i in range(days):
        # get the date string
        current_date = two_days_ago - timedelta(days=i)
        date_str = current_date.strftime('%m%d%y')

        # Decide which URLs to use based on the date
        if current_date < datetime(2025, 6, 1):
            urls = [
                f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2E2%2Epdf",
                f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2E1%2Epdf"
            ]
        else:
            # new urls after June 1, 2025
            urls = [
                f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2Epdf"
            ]

        combined_text = ""
        for url in urls:
            try:
                pdf_file = get_file(url)
                combined_text += get_text(pdf_file)
            except Exception as e:
                print(f"Warning: Failed to download or read PDF from {url}: {e}")
                # Continue to next URL without skipping the day

        if not combined_text:
            print(f"No PDFs available for {current_date.strftime('%Y-%m-%d')}, skipping...")
            
            # Save an empty JSON file for this date
            output_folder = "reports"
            output_filename = f"{output_folder}/crime_log_{current_date.strftime('%Y-%m-%d')}.json"
            os.makedirs(output_folder, exist_ok=True)
            with open(output_filename, "w") as json_file:
                json.dump([], json_file, indent=4)

            continue  # No data to process for this date, skip

        # create OpenAI prompt and get response
        prompt = create_prompt(combined_text, current_date)
        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )

        # parse the response
        entries_str = response.output_text
        try:
            entries = json.loads(entries_str)
        except json.JSONDecodeError as e:
            print("Failed to parse JSON from OpenAI response:")
            print(f"Error: {e}")
            print(f"Response content was:\n{entries_str}")
            break

        # add the entries to the all_entries list
        all_entries.extend(entries)

        # Save the JSON data to a file named by the current date
        output_folder = "reports"
        output_filename = f"{output_folder}/crime_log_{current_date.strftime('%Y-%m-%d')}.json"
        
        # Ensure the folder exists
        os.makedirs(output_folder, exist_ok=True)
        
        with open(output_filename, "w") as json_file:
            json.dump(entries, json_file, indent=4)

main()
