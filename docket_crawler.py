import os
import selenium
from selenium import webdriver
import time
import traceback
from urllib import urlencode
import urlparse

DOCKET_URL = os.getenv('DOCKET_URL')
MAX_TRIES = 5
WAIT_TIME = 3

class DocketCrawler(object):
    def __init__(self, base_url):
        self.driver = webdriver.Chrome('./chromedriver')
        self.base_url = base_url
        self.DOCKETS = 3 # [primary, supporting, comments]

    def end(self):
        self.driver.quit()

    def crawl(self):
        self.driver.get(self.base_url)
        docket_browsers = self.get_docket_browsers()
        hrefs = [link.get_attribute('href') for link in docket_browsers]
        
        amt = [6, 649, 11493] #the amounts expected in each documnet.

        for i, link in enumerate(hrefs):
            links = self.crawl_docket(link, total_expected=amt[i])
            print(links)

    def get_docket_browsers(self):
        links = []
        tries = 0
        while(len(links) < self.DOCKETS):
            links = self.driver.find_elements_by_link_text("View All")
            tries += 1
            time.sleep(WAIT_TIME)
            if tries > MAX_TRIES:
                break
        if len(links) > self.DOCKETS:
            raise Exception('Found too many Docket Browser links?')
        elif len(links) != self.DOCKETS:
            raise Exception('Could not find Docket Browser links')
        return links

    def crawl_docket(self, link, total_expected=25, per_page=25, links=None):
        if links is None:
            links = []

        url_parts = list(urlparse.urlparse(link))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        while True:
            link = urlparse.urlunparse(url_parts)
            self.driver.get(link)
            expected = min(total_expected, per_page)
            links += self.get_page_links(expected)
            total_expected -= len(links)
            if total_expected > 0:
                query['po'] = int(query['po']) + per_page
                url_parts[4] = urlencode(query)
            else:
                break
        return links

    def get_page_links(self, expected):
        hrefs = []
        tries = 0
        while len(hrefs) < expected and tries < MAX_TRIES:
            tries += 1
            time.sleep(WAIT_TIME)
            links = self.driver.find_elements_by_tag_name('a')
            hrefs = set([
                    link.get_attribute('href') for link in links
                    if link.get_attribute('href') 
                    and '/document?' in link.get_attribute('href')
            ])
        if len(hrefs) == expected:
            return hrefs
        else:
            raise Exception('Not all links found on ' + self.driver.current_url)

def main():
    try:
        c = DocketCrawler(DOCKET_URL)
        c.crawl()
    except Exception as e:
        print(e)
        traceback.print_exc()
    c.end()

if __name__ == '__main__':
    main()
