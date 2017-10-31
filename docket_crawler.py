from base64 import decodestring
from constants import IMAGE_BLACKLIST, BASIC_INFO_CLASS, ADDITIONAL_INFO_CLASS, METADATA_BLACKLIST
import datetime
import os
import requests
import selenium
from selenium import webdriver
import shutil
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

    def remove_folder(self, path):
        shutil.rmtree(path)

    def write_file(self, path, file_name, text):
        file_name = file_name.replace("/", "")
        file_name = file_name[:255]
        path = os.path.join(self.BASE_DIR, path, file_name)
        with open(path, 'w') as text_file:
            if isinstance(text, unicode):
                text = text.encode('utf-8')
            text_file.write(text)

    def write_links(self, links):
        file_name = self.BASE_DIR + "/links.txt"
        with open(file_name, 'w') as links_file:
            links_file.write("\n".join(links))

    def log_failed_links(self, links):
        file_name = self.BASE_DIR + '/failed_links.txt'
        with open(file_name, 'w') as links_file:
            links_file.write("\n".join([link[0] + ',' + link[1] for link in links]))

class ErrorLogger(object):
    def __init__(self, base_dir):
        self.error_file = base_dir + "/errors.txt"
        self.log_file = base_dir + "/log.txt"
        time = datetime.datetime.now()
        with open(self.error_file, 'w') as e_file:
            e_file.write(str(time) + '\n')
        with open(self.log_file, 'w') as log_file:
            log_file.write(str(time) + '\n')

    def log_error(self, message):
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        time = str(datetime.datetime.now())
        print('ERROR: ' + str(message))
        with open(self.error_file, 'a') as e_file:
            e_file.write("ERROR (" + time + "): " + str(message) + '\n')

    def log_warning(self, message):
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        time = str(datetime.datetime.now())
        print('WARNING: ' + str(message))
        with open(self.error_file, 'a') as e_file:
            e_file.write("WARNING (" + time + "): " + str(message) + '\n')

    def log_message(self, message):
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        print('MESSAGE: ' + str(message))
        with open(self.log_file, 'a') as log_file:
            log_file.write(str(message) + '\n')

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
        
        failed_links = []
        for i, link in enumerate(hrefs):
            links = self.crawl_docket(link)
            self.writer.write_links(links)
            path = self.writer.create_folder(self.DOCKETS[i])
            self.logger.log_message('Created ' + path)
            for j,doc_link in enumerate(links):
                if not self.crawl_document_page(doc_link, path):
                    failed_links.append((doc_link, path))
                self.logger.log_message('Finished ' + doc_link + '.  Documents crawled: ' + str(j+1) + '/' + str(len(links)))
            self.logger.log_message('Finished docket ' + str(i))
            self.logger.log_message(str(len(failed_links)) + '/' + str(len(links)) + ' Documents failed')
        return failed_links

    def retry(self, links):
        self.logger.log_message('Retrying ' + str(len(links)) + ' links')
        failed_links = []
        num = 0
        for link, path in links:
            num += 1
            if not self.crawl_document_page(link, path):
                failed_links.append((link, path))
            self.logger.log_message('Finished ' + link + '. Documents retried: ' + str(num) + '/' + str(len(links)))
        self.logger.log_message(str(len(failed_links)) + '/' + str(len(links)) + ' Documents failed')
        return failed_links

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
        self.logger.log_message('Found: ' + str(len(links)))
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
        path = None
        try:
            file_links = self.get_document_links()
            title = self.get_title()
            if len(title) > 255:
                title = title[:255]
            path = folder + '/' + title
            path = self.writer.create_folder(path)
            self.logger.log_message('Created ' + path)
            for i,link in enumerate(file_links):
                self.get_and_save_file(path, link, i)
            main_text = self.get_main_text()
            if main_text:
                self.logger.log_message('Writing ' + path + '/' + title + '.txt')
                self.writer.write_file(path, title + ".txt", main_text)
            comment = self.get_comment()
            if comment:
                self.logger.log_message('Writing ' + path + '/comment.txt')
                self.writer.write_file(path, 'comment.txt', comment)
            for image in self.get_images():
                self.logger.log_message('Writing ' + path + '/' + image['name'])
                self.writer.write_file(path, image['name'], image['content'])
            metadata = self.get_metadata()
            self.logger.log_message('Writing ' + path + '/metadata.txt')
            self.writer.write_file(path, 'metadata.txt', metadata)
            for file_data in self.get_attachment_metadata():
                self.logger.log_message('Writing ' + path + '/' + file_data['name'])
                self.writer.write_file(path, file_data['name'], file_data['content'])
            return True
        except Exception as e:
            self.logger.log_error("Crawl on " + link +  " failed.")
            self.logger.log_error(e.message)
            print(e)
            traceback.print_exc()
            if path:
                self.writer.remove_folder(path)
            return False

    def get_and_save_file(self, doc_name, link, i):
        doc = requests.get(link).content
        doc_id = urlparse.parse_qs(urlparse.urlparse(link).query)['documentId'][0]
        if 'contentType=excel12book' in link or 'contentType=excel8book' in link:
            extension = '.xls'
        elif 'contentType=pdf' in link:
            extension = '.pdf'
        elif 'contentType=msw8' in link or 'contentType=ms12' in link or "contentType=msw12" in link:
            extension = '.doc'
        elif 'contentType=ms_access' in link:
            extension = '.mdb'
        elif 'contentType=rtf' in link:
            extension = '.rtf'
        elif 'contentType=jpeg' in link:
            extension = '.jpg'
        elif 'contentType=ppt8' in link:
            extension = '.ppt'
        elif 'contentType=crtxt' in link or 'contentType=crtext' in link:
            extension = '.txt'
        elif 'contentType=bmp' in link:
            extension = '.bmp'
        elif 'contentType=tiff' in link:
            extension = '.tif'
        elif 'contentType=html' in link:
            extension = '.html'
        else:
            raise Exception('Unknown file type')

        self.logger.log_message('Writing ' + doc_name + '/' + doc_id + '_' + str(i) + extension)
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
                return main_text.strip()
            except Exception as e:
                #print(e)
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

    def get_comment(self):
        blocks = self.driver.find_elements_by_class_name("GIY1LSJIXD")
        text = "\n".join([block.text for block in blocks if block.text])
        return text

    def log_failed_links(self, links):
        self.writer.log_failed_links(links)

def main():
    start_time = time.time()
    if not DOCKET_URL:
        raise Exception('run: `export DOCKET_URL=<docket_url>`')
    try:
        l = ErrorLogger(RESULTS_DIR)
        c = DocketCrawler(DOCKET_URL, logger=l)
        failed_links = c.crawl()
        retries = 0
        while len(failed_links) and retries < MAX_TRIES :
            retries += 1
            print("Retrying " + str(retries) + "/" + str(MAX_TRIES))
            failed_links = c.retry(failed_links)
        if len(failed_links):
            print(str(len(failed_links)) + ' links failed to crawl.')
            c.log_failed_links(failed_links)
    except Exception as e:
        print("FATAL ERROR:")
        print(e)
        l.log_error("FATAL:")
        l.log_error(e.message)
        traceback.print_exc()
    c.end()
    total_time = time.time() - start_time 
    print('Total time: ' + str(total_time))

if __name__ == '__main__':
    main()
