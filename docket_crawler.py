from base64 import decodestring
import os
import requests
import selenium
from selenium import webdriver
import time
import traceback
from urllib import urlencode
import urlparse

#DOCKET_URL = os.getenv('DOCKET_URL')
DOCKET_URL = "https://www.regulations.gov/docket?D=EPA-HQ-RCRA-2009-0640"
MAX_TRIES = 5
WAIT_TIME = 3

RESULTS_DIR = '../crawl_results'

IMAGE_BLACKLIST = [
        u'https://www.regulations.gov/images/logo.png',
        u'https://www.regulations.gov/images/icon-search.png',
        u'https://www.regulations.gov/images/fileicons/small/icon_pdf.gif',
        u'https://www.regulations.gov/images/icon_pop-out.png',
        u'https://www.regulations.gov/images/clip_paper_icon.png',
        u'https://www.regulations.gov/images/clip_paper_icon.png',
        u'https://www.regulations.gov/images/clip_paper_icon.png',
        u'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAhCAYAAAC4JqlRAAAE7klEQVR42sWX209cVRTG9zswzOXMYExqSIxNTIwPjYkxfTAxqaX/gc/axqTAcJky3IVSKLcC1tpiQowvJNYaq0ZNa7ViaCpe0lotXhqgQrkNcztz5nKGGWA+1zrc5nAObTUBdvJlmP3tvX5rr7P3PoMQ1MZKc1/+x5N7fdKbF5uszsOOihjMYiazxXhFTtFMQz6CbXYo3RKiPTsrZjCLmcwW8637JpRuBxbPuZC+UICl/p0VM5jFTGaLUHtBJrkG300xM3RayohIhwPpc9T57i6LmMwWynoCeyClU+IEJKTeKTAo+bYLmWQYy747SN/9EOmRbqQuHkbqbIHp+P8jZgulXVoNukWxLglmbUWZRvrHXix+8KLpvP8iZotIG52APpdB3P/QtpxC+tYAkuf3m85/HDFDRFopgV6XQQqZync9iN76GMmp29vmkVlUkLpWhWSPyzTOw8RsIZ9yIHnGZVCMyuNvtGHGa8GUJw9TDYXwf1QGdfymaSLpPy4j0bvPNNZ2YraQT1ICXS6D1E4X4qediLZKiLQ4EGqyw1dnxQOPBbNnD2Nx+jdDEktTI1D7njaNZyZmi3CzQ4M9SokOqkqbU5u0UG+jqljgv1SJzFJKX4mJIcQ7nnismMwWYVqZ2u40KN62egqW53/H0t9XkPz8OK1uPxJUlRhVRaZ5c958rRrL8bAuicWfBrRxZnGzxWwRbqQEaGVbFWkynoJMOonUcA8SXYVItDqh0AoWaqyYaXkey9GAbqz6aYk2xiz2upgtQvV2JE45DeL+7dpKdAGJgVcRb6E90kyblZKY6zukexwriTCiHc+Yxs5miGCdXQu0VWwGL7oR/KoTycnbptWID76G2EmqRJMEn9cK/+BxfRVu9pMvmcZnMVsEaymBZqdBSqOEhSobpsstmCzJw4PWlxAfvWZIInbhFcSa6JE1ODBXmY/En9c3fbqslDMHTOOzmC0C1TbE3pIMilICHFSmLIM1Nvg8Vi2RwOVG/YUoT0NpeUobz+PmOw7q/MSNfigUx4zBbBGgVcYapEdKqXMg6KWLyW1B8LNmPeTrdkTrV8f4Kq1Q//petxfkOqdpTGaLwAmbNtlUXQeQHh9evWQmf6ZyvkBJ2DFdaoF6bzjrOo5DbnhSm8N+YLBYl2Dk/BHT+MwWAQ8lUCsZFKl2IHVvSH/J3B+BTP08Z65NX2pl8BiUGrofvPRTq6YQmZS64cWudmrxtjI4jghUUALVkkEhj11bmW7T0TELVdGGqyKIOx/q2A+bO/6XS5CpX/HS5i23IpnlJe9eRfiEw8BgtvDTYMXrMIhNNWtHa4EoqL/CuuHLX7ZveCl6N4QqbRueMvTe5jvCP4HgmpctZgu/mwJSdlsVLLdhtvZZxO5c0YLER7/FTP1zWj/7oQo6He+/vrnZVAWBsnWPkvukIeu4qhtetpgtFkqtiHgcBoUr6e1H3uSbeRg/mqN98nfu13xKYK44H/eP5WLsjRxMkc8Q9ji5WfImjhq9bDFbLJRQAhUOU4XLaUe7bfCX2LRP/r7uyeUEKrPDX2oDxwiUbvrsBd12bd5WL1vsCV+xVZuwF2K28JXYIZftjZgtAm0HMzKVay/EbKH++sV4kJ5VuNS+q2ImswWdkkOLo98g0nsEYTf9SKCy7KiIwSxmMlv7F53+KCLd4Jcbdr4tr7GKmP0vi5tvNuFm4WMAAAAASUVORK5CYII=',
        u'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAhCAYAAAC4JqlRAAAEP0lEQVR42sWY+VMTZxjH33+uM/5SpYBEUbTaMgqttFBrKYPaQdtivRjsMdNW247tdMbyA1CZSoDKkDuBXOSAkHBqjoVNNtkcAtFv3yeByLFILALPzGezefO+38+z2d3JwRivM/3xA3WDcVP9UBwNuww5yEVOcrNavtOkT+C6LYn20RS+c+8u5CAXOcnNWszJqXZXEr9MpHB/Mo3fdxlykIuc5GatNvnF3Yk0fgvsLeQkN7vpTOKen3e1x5CT3OwG3/zMu9kPyM2uO2X8yM/JfkBu1uqQ8YMv9Ua4H0ihczaN78eTRc0nN/vSLuNbvmAn3PEm4BIzWK34Yhbtnvi268jNWvimbSy5idteGQ+mU/zWye8rzcnN8ySgDSWxtrxCAn9OxF65jiA3u2yTcdOb3MR1lwRNMB8sPcti4GkKd8bWz73hkXFvLIatqmdGzs1RyifIzS5aE/iGT9rI184obllmkV7KFgIz2efQhFJo8+bXtI7GMCVl8Kr6KxDHNbeyg9zs85EEvnLLm7jqlNCsm4EzGN0Umll+jt4n/O13CNiuopllXLGLig5ys8+GE7jikhVpNoUgpha3Dk8voZi661lAizPObz1+3kdf+sjNzlviuMwHlWiyRHBN68NCMoM3UbpwChft0UI+uVm9OY5mZ0KRJquI+sEAdNPCjuVzUgpOQUajRSjkk5vVmSU0OuLK2CU0GILon9xZA0OBILo8c7ik8eO8OVLIJzf7wCThU3t8SxrMAv/cHselPgemxcT/auDcQytq+sbwke4JPhkRC9nkZmdNMdTzI92Kj61RnDOGUM0DUkvLry1/5Avi7GM/P9oIzxLXZZObVRtjqLNJeawxtPsSucfC2Mp4je4pGvpGkVwsvgmBX7y1ajdqjeH1eSuQm502xFBrlXLUDIv41R+HTkjjqpuPjeRfa7DF+LeYGObTi0XLqdHGARfeG5zO5a461kJudlIfxRkuIqrN8zg1NIuf3OEdXXQROY0LaidO9PlQbRIK+RshN6vSRfH+cCyPJYpT+jCO903gC37/R5LPXlve7ZnFya4RHFP7+BFGcpmF/A2Qmx3VRvGuJfYScxRV2hBUveN4p8OMNp0XgW2u/jA/4k73LKq7h1He7UDlwBROGIRc1rrsDZCbqbQiqki6FpOIY/oIjjyeQVmPG4c6LFB1GNCotqOx14Y/7JO4pfPk9k93mnHwgRGlXQ5UqCdQqQniuHF+c6YC5GblGhGVpqgyRhFHtGFUDM6hvH8SpY/4u9LjRcnfLpQ8dKP0n3GUqf04/O8MVJoQjhrmt85SgNysdIhLjEVgWIBKL6CCGuIyQqWL8LH54tYrQG5WwjeHjftDyWoDZYb9IdfAhxbpRYmeP9kHyM30wqL/be0CDur3FnKSm/Hb+K1hcQkXHBIO0Qu63YUc5CInuXM/0fnOAY6Gk8XuV3bFlft/4D+oXdznons4MgAAAABJRU5ErkJggg==',
        u'https://www.regulations.gov/images/external-link_brown.png',
]

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

class DocketCrawler(object):
    def __init__(self, base_url, writer=FileWriter(RESULTS_DIR)):
        self.writer = writer
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
        except Exception as e:
            #TODO: write to file or ensure this is suppossed to happen somehow
            print(e)
            traceback.print_exc()
            import pdb; pdb.set_trace()
        file_links = self.get_document_links()
        for link in file_links:
            self.get_and_save_file(doc_name, link)

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
        raise Exception('No documents found on ' + self.driver.current_url)

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
        raise Exception('No Text on ' + self.driver.current_url)

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

def main():
    if not DOCKET_URL:
        raise Exception('run: `export DOCKET_URL=<docket_url>`')
    try:
        c = DocketCrawler(DOCKET_URL, FileWriter(RESULTS_DIR))
        c.crawl()
    except Exception as e:
        print(e)
        traceback.print_exc()
    c.end()

if __name__ == '__main__':
    main()
