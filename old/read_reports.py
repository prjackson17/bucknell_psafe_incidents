"""
Parker Jackson
Nov 2024
Reading Bucknell Public Safety info
Test file to get started, prints out info from PDF
"""

import io
import json
import requests
from datetime import datetime, timedelta
import fitz
import urllib3
from openai import OpenAI
from prettytable import PrettyTable

# Initialize OpenAI API
client = OpenAI()

# Disable warnings from unverified website
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'
}

two_days_ago = datetime.now() - timedelta(days=4)
date_str = two_days_ago.strftime('%m%d%y')

# url = f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2E2%2Epdf"
# url2 = f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2E1%2Epdf"
url = f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2Epdf"

response = requests.get(url, headers=headers, verify=False)
if response.status_code == 200:
    pdf_file = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")
else:
    raise Exception("Failed to download the PDF from URL1")

text = ""
for page in pdf_file:
    text += page.get_text()

prompt = f"""
You are a data assistant. Extract the crime log data from the following text and return it as a Python array of objects.
Each object must have keys: Date (MM/DD/YYYY), Time, Location, Nature, Case Number, and Disposition. Just return the data.

Raw text:
{text}
"""

response = client.responses.create(
    model="gpt-4.1",
    input=prompt
)

entries_str = response.output_text
entries = json.loads(entries_str)

# Print as table
table = PrettyTable()
table.field_names = ["Date", "Time", "Location", "Nature", "Case Number", "Disposition"]

for entry in entries:
    table.add_row([
        entry.get("Date", ""),
        entry.get("Time", ""),
        entry.get("Location", ""),
        entry.get("Nature", ""),
        entry.get("Case Number", ""),
        entry.get("Disposition", "")
    ])

print(table)