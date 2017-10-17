from base64 import decodestring
from constants import IMAGE_BLACKLIST, BASIC_INFO_CLASS, ADDITIONAL_INFO_CLASS
import os
import requests
import selenium
from selenium import webdriver
import time
import traceback
from urllib import urlencode
import urlparse

DOCKET_URL = os.getenv('DOCKET_URL')
MAX_TRIES = 5
WAIT_TIME = 3

RESULTS_DIR = '../crawl_results'


class FileWriter(object):
    def __init__(self, base_dir):
        self.BASE_DIR = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def create_folder(self, path):
        path = os.path.join(self.BASE_DIR, path)
        print('Creating: ', path)
        if not os.path.exists(path):
            os.makedirs(path)

    def write_file(self, path, file_name, text):
        path = os.path.join(self.BASE_DIR, path, file_name)
        print('Writing: ', path)
        with open(path, 'w') as text_file:
            if isinstance(text, unicode):
                text = text.encode('utf-8')
            text_file.write(text)

class ErrorLogger(object):
    def __init__(self, base_dir):
        self.error_file = base_dir + "/errors.txt"
        with open(self.error_file, 'w') as e_file:
            e_file.write('Errors:')

    def log_error(self, message):
        print(message)
        with open(self.error_file, 'a') as e_file:
            e_file.write("ERROR:" + message)

    def log_warning(self, message):
        print(message)
        with open(self.error_file, 'a') as e_file:
            e_file.write("WARNING: " + messaage)

class DocketCrawler(object):
    def __init__(self, base_url, writer=FileWriter(RESULTS_DIR), logger=ErrorLogger(RESULTS_DIR)):
        self.writer = writer
        self.logger = logger
        self.driver = webdriver.Chrome('./chromedriver')
        self.base_url = base_url
        self.DOCKETS = 3 # [primary, supporting, comments]

    def end(self):
        self.driver.quit()

    def crawl(self):
        self.driver.get(self.base_url)
        docket_browsers = self.get_docket_browsers()
        hrefs = [link.get_attribute('href') for link in docket_browsers]
        
        for i, link in enumerate(hrefs):
            links = self.crawl_docket(link)
            for doc_link in links:
                self.crawl_document_page(doc_link)
            print('Finished docket ', i)

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

    def get_amount_of_documents(self, link):
        self.driver.get(link)
        tries = 0
        while tries < MAX_TRIES:
            tries += 1
            time.sleep(WAIT_TIME)
            elements = self.driver.find_elements_by_xpath("//*[contains(text(), 'results')]")
            if len(elements) == 1:
                return int(elements[0].text.split(' ')[0])
        raise Exception("Could not find amt expected")

    def crawl_docket(self, link, per_page=25):
        total_expected = self.get_amount_of_documents(link)
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

    def crawl_document_page(self, link):
        doc_name = link.split('?')[-1]
        self.writer.create_folder(doc_name)
        self.driver.get(link)
        try:
            main_text = self.get_main_text()
            self.writer.write_file(doc_name, 'main.txt', main_text)
            for image in self.get_images():
                self.writer.write_file(doc_name, image['name'], image['content'])
            metadata = self.get_metadata()
            self.writer.write_file(doc_name, 'metadata.txt', metadata)
            file_links = self.get_document_links()
            for link in file_links:
                self.get_and_save_file(doc_name, link)
        except Exception as e:
            self.logger.log_error("Crawl on " + link +  " failed.")
            self.logger.log_error(e)
            print(e)
            traceback.print_exc()

    def get_and_save_file(self, doc_name, link):
        doc = requests.get(link).content
        doc_id = urlparse.parse_qs(urlparse.urlparse(link).query)['documentId'][0]
        self.writer.write_file(doc_name, doc_id, doc)

    def get_document_links(self):
        tries = 0
        while tries < MAX_TRIES:
            tries += 1
            elements = [
                    element.get_attribute('href') for element 
                    in self.driver.find_elements_by_xpath("//a") 
                    if element.get_attribute('href') 
                    and 'documentId' in element.get_attribute('href')
            ]
            if elements:
                return elements
            time.sleep(WAIT_TIME)
        self.logger.log_error("No documents found on " + self.driver.current_url)
        return None

    def get_main_text(self):
        tries = 0
        while tries < MAX_TRIES:
            tries += 1
            try:
                main_text = self.driver.find_element_by_class_name("gwt-HTML").text
                return main_text
            except Exception as e:
                print(e)
                time.sleep(WAIT_TIME)
        self.logger.log_warning('No Text Found on ' + self.driver.current_url)
        return None

    def get_images(self):
        imgs = self.driver.find_elements_by_tag_name("img")
        srcs = [img.get_attribute('src') for img in imgs if img.get_attribute('src') ]

        img_num = 0
        srcs_dicts = []
        for src in srcs:
            if src not in IMAGE_BLACKLIST:
                if "data:image/png" in src:
                    content = decodestring(src.split(',')[1])
                    name = 'image_' + str(img_num)
                    img_num += 1
                else:
                    content = requests.get(src).content
                    name = '-'.join(urlparse.urlparse(src).path.split('/'))
                srcs_dicts.append({
                    'name': name,
                    'content': content,
                })
        return srcs_dicts

    def get_metadata(self):
        basic_info_elements = self.driver.find_elements_by_class_name(BASIC_INFO_CLASS)
        details_switch = self.driver.find_element_by_link_text("Show More Details  ")
        details_switch.click()
        additional_info_elements = self.driver.find_elements_by_class_name(ADDITIONAL_INFO_CLASS)
        text = [element.text for element in basic_info_elements + additional_info_elements]
        return '\n'.join(text)

def main():
    if not DOCKET_URL:
        raise Exception('run: `export DOCKET_URL=<docket_url>`')
    try:
        l = ErrorLogger(RESULTS_DIR)
        c = DocketCrawler(DOCKET_URL, logger=l)
        c.crawl()
    except Exception as e:
        print("FATAL ERROR:")
        print(e)
        l.log_error(e)
        traceback.print_exc()
    c.end()

if __name__ == '__main__':
    main()
