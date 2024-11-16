"""
Parker Jackson
Nov 2024
Reading Bucknell Public Safety info
Test file to get started, prints out info from PDF
"""

import io
import requests
from datetime import datetime, timedelta
from PyPDF2 import PdfReader
from crime_date import CrimeDate, Incident
import urllib3

# disable warnings from unverified website
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}

two_days_ago = datetime.now() - timedelta(days=11)

# Format the date as MMDDYY
date_str = two_days_ago.strftime('%m%d%y')

url = f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2E2%2Epdf"
url2 = f"https://www1.bucknell.edu/script/PublicSafety/file.asp?f=crime+log+{date_str}%2E1%2Epdf"

response = requests.get(url=url, headers=headers, timeout=120, verify=False)
on_fly_mem_obj = io.BytesIO(response.content)
pdf_file = PdfReader(on_fly_mem_obj)

crime_reports = []

for page_num in range(len(pdf_file.pages)):
    page = pdf_file.pages[page_num]
    text = page.extract_text()

    # print(text)

    split_text = text.splitlines()

    # print(split_text[-2].split()[-1])

    for i, line in enumerate(split_text):
        print(i, line)

# # Print the crime reports
# for report in crime_reports:
#     print(report)

"""
# 0 Bucknell University Public Safety/Police
# 1 Clery Daily Crime Log
# 2 Lewisburg
# 3 Monday, November 11, 2024
# 4 Occurred Case Number Location DispositionDate Time
# 5 ReportedTime
# 6 Nature of Crime Occurred
7 McDonnell Hall Case Under 
8 Investigation11/11/2024  13:25 Disorderly 
9 Conduct2024-14679 11/11/2024 13:25 -
10 Other Offenses-
11 Total Selected = 1
12 11/12/2024 Informant PS Page 1 of 1
"""
"""
# 0 Bucknell University Public Safety/Police
# 1 Clery Daily Crime Log
# 2 Lewisburg
# 3 Tuesday, November 05, 2024
# 4 Occurred Case Number Location DispositionDate Time
# 5 ReportedTime
# 6 Nature of Crime Occurred
7 Roberts Hall Case Under 
8 Investigation11/5/2024  12:29 Disorderly 
9 Conduct2024-14350 11/5/2024 12:29 -
10 Other Offenses-
11 On campus Open 11/5/2024  12:54 Forcible Rape 2024-14353 11/5/2024 12:54 -
12 Clery sexual assualt
13 Total Selected = 2
14 11/6/2024 Informant PS Page 1 of 1
"""