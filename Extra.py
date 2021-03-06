import urllib
import re
import urllib.request as urllib2
from bs4 import BeautifulSoup as bf
import time
import csv
import lxml
from lxml import html

url = "https://www.newtral.es/factcheck-falso-confinamiento-espana-severo-abascal/20201007/"
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome" \
             "/86.0.4240.183 Safari/537.36"
headers = {"User-Agent": user_agent}
request = urllib2.Request(url, None, headers)
response = urllib2.urlopen(request, timeout=30)  # urlopen(url, data, timeout)
page = response.read()

# # lxml parser & page printer
# document_root = html.fromstring(page)
# print(lxml.etree.tostring(document_root, encoding='unicode', pretty_print=True))

soup = bf(page, features="html.parser")
html_plaintext = page

# convert html to text
# kill all script and style elements
for script in soup(["script", "style"]):
    script.extract()  # rip it out

# get text
text = soup.get_text()

# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())
# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
text = '\n'.join(chunk for chunk in chunks if chunk)

print(text)