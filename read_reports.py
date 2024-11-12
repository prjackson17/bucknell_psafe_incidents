"""
Parker Jackson
2024
Reading Bucknell Public Safety info
"""

import io
import requests
from datetime import datetime, timedelta
from PyPDF2 import PdfReader
from crime_report import CrimeReport

headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}

# Calculate the date two days ago
two_days_ago = datetime.now() - timedelta(days=2)

# Format the date as MMDDYY
date_str = two_days_ago.strftime('%m%d%y')

url = f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2E2%2Epdf"
response = requests.get(url=url, headers=headers, timeout=120, verify=False)
on_fly_mem_obj = io.BytesIO(response.content)
pdf_file = PdfReader(on_fly_mem_obj)
print(url)

crime_reports = []

for page_num in range(len(pdf_file.pages)):
    page = pdf_file.pages[page_num]
    text = page.extract_text()

    for line in text.splitlines():
        invalid_lines = ['']
        print(line)

# # Print the crime reports
# for report in crime_reports:
#     print(report)