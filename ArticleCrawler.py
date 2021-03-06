import urllib
import re
import urllib.request as urllib2
from bs4 import BeautifulSoup as bf
import time
import csv
import lxml
import pandas as pd
from lxml import html
from pandas import read_csv
import socket
import articleDateExtractor

# alter following two row of code if you don't want to restart crawling
# i = 2
# for index, row in df.iterrows():

fields = ['content', 'accuracy', 'date', 'region', 'explanation', 'reference_url', 'reference_html', 'reference_text']
filename = 'ExampleofOneEntry.csv'
i = 2  # count the index of row in csv file (including header) # alter this field if it's not the fist time
df = read_csv('PoynterCovid19Database.csv')
with open(filename, 'w') as csvfile:                 # the first time run this crawler
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()

for index, row in df[0:1].iterrows():
    # print(index, row['content'], row['accuracy'], row['date'], row['region'], row['explanation'],
    # row['reference_url'])
    data = []
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome" \
                 "/86.0.4240.183 Safari/537.36"
    headers = {"User-Agent": user_agent}

    while True:
        try:
            request = urllib2.Request(row['reference_url'], None, headers)
            response = urllib2.urlopen(request, timeout=10)  # urlopen(url, data, timeout)
            page = response.read()

            soup = bf(page, features="html.parser")

            # lxml parser & page printer
            # document_root = html.fromstring(page)
            # html_plaintext = lxml.etree.tostring(document_root, encoding='unicode', pretty_print=True)

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
        except ValueError:
            print("===============!!!!!!!!!!!!!!!!!!================")
            print('i=' + str(i))
            print('null link!')
        except urllib.error.HTTPError:
            print("===============!!!!!!!!!!!!!!!!!!================")
            print('i=' + str(i))
            print('HTTP Error 404: Not Found')
        except urllib.error.URLError:
            print("===============!!!!!!!!!!!!!!!!!!================")
            print('i=' + str(i))
            print('URLError: This site can’t be reached!')
        except socket.timeout:
            continue
        break


    try:
        data.append({'content': row['content'], 'date': row['date'], 'region': row['region'],
                     'accuracy': row['accuracy'], 'explanation': row['explanation'],
                     'reference_url': row['reference_url'], 'reference_html': html_plaintext,
                    'reference_text': text})
    except IndexError:
        print("===============!!!!!!!!!!!!!!!!!!================")
        print('i=' + str(i))
        print('other issues!')
    except NameError:
        print("===============!!!!!!!!!!!!!!!!!!================")
        print('i=' + str(i))
        print('Attribute(s) remains empty!')

    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        for item in data:
            writer.writerow(item)

    # print('i =', i)
    i = i + 1

    time.sleep(1)
