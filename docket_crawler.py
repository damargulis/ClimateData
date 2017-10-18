from base64 import decodestring
from constants import IMAGE_BLACKLIST, BASIC_INFO_CLASS, ADDITIONAL_INFO_CLASS, METADATA_BLACKLIST
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
WAIT_TIME = 1

RESULTS_DIR = '../crawl_results'


class FileWriter(object):
    def __init__(self, base_dir):
        self.BASE_DIR = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def create_folder(self, path):
        path = os.path.join(self.BASE_DIR, path)
        path = os.path.normpath(path)
        print('Creating: ', path)
        if not os.path.exists(path):
            os.makedirs(path)
            return path
        else:
            attempt = 0 
            while os.path.exists(path + '_' + str(attempt)):
                attempt += 1
            path = path + '_' + str(attempt)
            os.makedirs(path)
            return path

    def write_file(self, path, file_name, text):
        file_name = file_name.replace("/", "")
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
            e_file.write('Errors:\n')

    def log_error(self, message):
        print(message)
        with open(self.error_file, 'a') as e_file:
            e_file.write("ERROR:" + str(message) + '\n')

    def log_warning(self, message):
        print(message)
        with open(self.error_file, 'a') as e_file:
            e_file.write("WARNING: " + str(message) + '\n')

class DocketCrawler(object):
    def __init__(self, base_url, writer=FileWriter(RESULTS_DIR), logger=ErrorLogger(RESULTS_DIR)):
        self.writer = writer
        self.logger = logger
        self.driver = webdriver.Chrome('./chromedriver')
        self.base_url = base_url
        self.DOCKETS_NUM = 3 
        self.DOCKETS = ['Primary Documents', 'Supporting Documents', 'Comments']


    def end(self):
        self.driver.quit()

    def crawl(self):
        self.driver.get(self.base_url)
        docket_browsers = self.get_docket_browsers()
        hrefs = [link.get_attribute('href') for link in docket_browsers]
        
        for i, link in enumerate(hrefs):
            links = self.crawl_docket(link)
            path = self.writer.create_folder(self.DOCKETS[i])
            for j,doc_link in enumerate(links):
                self.crawl_document_page(doc_link, path)
                print('Finished ' + doc_link + '.  Documents crawled: ' + str(j+1) + '/' + str(len(links)))
            print('Finished docket ', i)

    def get_docket_browsers(self):
        links = []
        tries = 0
        while(len(links) < self.DOCKETS_NUM):
            links = self.driver.find_elements_by_link_text("View All")
            tries += 1
            time.sleep(WAIT_TIME)
            if tries > MAX_TRIES:
                break
        if len(links) > self.DOCKETS_NUM:
            raise Exception('Found too many Docket Browser links?')
        elif len(links) != self.DOCKETS_NUM:
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
                text = elements[0].text.split(' ')[0]
                text = ''.join(text.split(','))
                return int(text)
        raise Exception("Could not find amt expected")

    def crawl_docket(self, link, per_page=25):
        total_expected = self.get_amount_of_documents(link)
        print('expected: ', total_expected)
        links = []
        url_parts = list(urlparse.urlparse(link))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        while True:
            link = urlparse.urlunparse(url_parts)
            self.driver.get(link)
            expected = min(total_expected, per_page)
            links += self.get_page_links(expected)
            total_expected -= expected
            if total_expected > 0:
                query['po'] = int(query['po']) + per_page
                url_parts[4] = urlencode(query)
            else:
                break
        print('Found:', len(links))
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
            missing = str(expected - len(hrefs))
            self.logger.log_error(missing + " links found missing on " + self.driver.current_url)
            return hrefs

    def crawl_document_page(self, link, folder):
        self.driver.get(link)
        try:
            file_links = self.get_document_links()
            title = self.get_title()
            path = folder + '/' + title
            path = self.writer.create_folder(path)
            for i,link in enumerate(file_links):
                self.get_and_save_file(path, link, i)
            main_text = self.get_main_text()
            if main_text:
                self.writer.write_file(path, title + ".txt", main_text)
            for image in self.get_images():
                self.writer.write_file(path, image['name'], image['content'])
            metadata = self.get_metadata()
            self.writer.write_file(path, 'metadata.txt', metadata)
            for file_data in self.get_attachment_metadata():
                self.writer.write_file(path, file_data['name'], file_data['content'])
        except Exception as e:
            self.logger.log_error("Crawl on " + link +  " failed.")
            self.logger.log_error(e.message)
            print(e)
            traceback.print_exc()

    def get_and_save_file(self, doc_name, link, i):
        doc = requests.get(link).content
        doc_id = urlparse.parse_qs(urlparse.urlparse(link).query)['documentId'][0]
        if 'contentType=excel12book' in link or 'contentType=excel8book' in link:
            extension = '.xls'
        elif 'contentType=pdf' in link:
            extension = '.pdf'
        else:
            raise Exception('Unknown file type')
        self.writer.write_file(doc_name, doc_id + '_' + str(i) + extension, doc)

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
        self.logger.log_warning("No documents found on " + self.driver.current_url)
        return []

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
        doc_id = (self.driver.current_url.split('?')[-1]).split('=')[-1]
        basic_info_elements = self.driver.find_elements_by_class_name(BASIC_INFO_CLASS)
        details_switch = self.driver.find_element_by_link_text("Show More Details  ")
        details_switch.click()
        time.sleep(WAIT_TIME)
        additional_info_elements = self.driver.find_elements_by_class_name(ADDITIONAL_INFO_CLASS)
        text = [element.text for element in basic_info_elements + additional_info_elements]
        text = [line for line in '\n'.join(text).split('\n') if line not in METADATA_BLACKLIST]
        text = ['Document Id: ' + doc_id] + text
        return '\n'.join(text)

    def get_title(self):
        title = self.driver.find_element_by_class_name("GIY1LSJBID").text
        title = title.replace("/", "-")
        return title
    
    def get_attachment_metadata(self):
        info_buttons = self.driver.find_elements_by_link_text("+ View more information")
        for button in info_buttons:
            tries = 0
            while tries <= MAX_TRIES:
                tries += 1
                try:
                    button.click()
                    break
                except Exception as e:
                    time.sleep(WAIT_TIME)
                    continue
                raise Exception("Could not get all information panels")
        information_panels = self.driver.find_elements_by_class_name("GIY1LSJGVD")
        titles = self.driver.find_elements_by_class_name("GIY1LSJL1D")
        if len(titles) != len(information_panels):
            raise Exception("Information panels mismatch")
        return [{
            'name': titles[i].text + ".txt",
            'content': information_panels[i].text
        } for i in range(len(titles)) ]

def main():
    start_time = time.time()
    if not DOCKET_URL:
        raise Exception('run: `export DOCKET_URL=<docket_url>`')
    try:
        l = ErrorLogger(RESULTS_DIR)
        c = DocketCrawler(DOCKET_URL, logger=l)
        c.crawl()
    except Exception as e:
        print("FATAL ERROR:")
        print(e)
        l.log_error(e.message)
        traceback.print_exc()
    c.end()
    total_time = time.time() - start_time 
    print('Total time: ' + str(total_time))

if __name__ == '__main__':
    main()
