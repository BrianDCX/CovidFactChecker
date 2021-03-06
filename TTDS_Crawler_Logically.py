##
import urllib
import re
import urllib.request as urllib2
from bs4 import BeautifulSoup as bf
import time
import csv
import lxml
from lxml import html

# create a file for restoring data
fields = ['content', 'credibility', 'date', 'region', 'explanation','reference_URL']
filename = 'Logically_database.csv'
# with open(filename, 'w') as csvfile:
#     writer = csv.DictWriter(csvfile, fieldnames=fields)
#     writer.writeheader()


# change the page num of website
for page_num in range(1,2):
    url = "https://www.logically.ai/factchecks/library/page/"+ str(page_num)
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome" \
                 "/86.0.4240.183 Safari/537.36"
    headers = {"User-Agent": user_agent}
    request = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(request, timeout=30)  # urlopen(url, data, timeout)
    page = response.read()

    # # lxml parser & page printer
    # document_root = html.fromstring(page)
    # print(lxml.etree.tostring(document_root, encoding='unicode', pretty_print=True))



    # extract info
    soup = bf(page, 'html.parser')
    data = []
    date_list = []
    region_list = []
    ref_list = []
    credibility_list = []
    content_list = []
    explanation_list = []
    claims_node_list = soup.find_all('article', attrs={'class': 'grid-item-4'})  # find the correct node
    for claim in claims_node_list[0:1]:
        # IMPORTANT: '+' is greedy, which means it will match as more content as possible, use "+?"(not greedy mode) instead

        # extract the explanation and reference URL
        link_ref_page = re.findall(r'(?<=href=").+?(?=")', str(claim))
        url_ref_page = str(link_ref_page[0])
        print(url_ref_page)  # find the URL in the list page
        request_ref_page = urllib2.Request(url_ref_page, None, headers)
        response_ref_page = urllib2.urlopen(request_ref_page, timeout=30)  # urlopen(url, data, timeout)
        ref_page = response_ref_page.read()
        ref_page_soup = bf(ref_page, 'html.parser')
        ref_node = ref_page_soup.find_all('div', attrs={'class': 'blog-post__body'})
        print(str(ref_node))

##
        explanation = re.findall(r'(?<=Explanation: ).+?(?=</p>)', str(ref_node))
        explanation_list.append(explanation)
        ref_link = re.findall(r'(?<=href=").+?(?=" target)', str(ref_node))
        ref_list.append(ref_link)

        # extract the date and region
        date_node = ref_page_soup.find_all('p', attrs={'class': 'entry-content__text entry-content__text--topinfo'})
        date = re.findall(r'(?<=<strong>).+?(?= \|)', str(date_node))
        date_list.append(date)
        region = re.findall(r'(?<=\| ).+?(?=</strong>)', str(date_node))
        region_list.append(region)

        # extract content and credibility
        credibility = re.findall(r'(?<=<span class="entry-title--red">).+?(?=:</span>)', str(claim))
        credibility_list.append(credibility)
        content = re.findall(r'(?<=</span> ).+?(?=</a>)', str(claim))
        content_list.append(content)
        time.sleep(5)

    i = 0
    for item in content_list:
        try:
            data.append({'content': content_list[i][0], 'date': date_list[i][0], 'region': region_list[i][0],
                         'credibility': credibility_list[i][0], 'explanation': explanation_list[i][0], 'reference': ref_list[i][0]})
        except IndexError:
            print("===============!!!!!!!!!!!!!!!!!!================")
            print('i=' + str(i))
            print('page_num='+str(page_num))

        i = i + 1
    with open(filename, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        for item in data:
            writer.writerow(item)
