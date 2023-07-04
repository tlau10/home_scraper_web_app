import requests
from bs4 import BeautifulSoup
from home_scraper_helper import read_json_file, write_json_file
import configparser
import re
from data_classes import ScraperData

config = configparser.ConfigParser()
config.read("home_scraper.ini")

WEBSITE = config["files"]["website"]
LIST = config["files"]["list"]
CITIES = ["Überlingen", "Meersburg", "Friedrichshafen", "Uhldingen", "Ueberlingen"]

class WebScraper():
    """General Scraper class"""

    def __init__(self, scraper_object):
        self.scraper_data = scraper_object 

    def scrape(self):
        """start scraping"""
        urls = self.scraper_data.get_urls()
        html_tag = self.scraper_data.get_html_tag()
        page_title = self.scraper_data.get_page_title()
        found_items = self.scraper_data.get_found_items()

        for url in urls:
            print(url)
            page = self.make_request(request_url = url)
            tags = self.parse_html(html = page, tag=html_tag)

            for a_tag in tags:
                # skip tags with wrong city
                if self.no_valid_city(tag = a_tag):
                    continue

                a_tag = a_tag.find("a") if page_title == "immonet" or page_title == "wohnungsboerse" or page_title == "immobilo" else a_tag
                link_url = self.extract_url(a_tag = a_tag, page_title = page_title)
                link = self.build_link(url = link_url, page_title = page_title)

                found_items.append(link)
                print(link)

        self.save_items()
    
    def make_request(self, request_url):
        """
        make http request to given url
        @param request_url: url to request html content from
        @returns: html content
        """
        return requests.get(url = request_url, headers = self.scraper_data.get_http_header())

    def parse_html(self, html, tag):
        """
        parse html page to find given tags
        @param html: html page
        @param tag: tags to find in html, eg.: <div>
        @returns: list of found tags
        """
        soup = BeautifulSoup(html.content, "html.parser")
        return soup.find_all(tag, class_ = self.scraper_data.get_html_class())

    def extract_url(self, a_tag, page_title):
        """
        Extract link from given a_tag by extracting specific html class, eg.: href
        @param a_tag: <a> tag from search result
        @param page_title: title of page search result belongs to, eg.: ebay; is set on class initialization
        @returns: url
        """
        html_class = "data-href" if page_title == "ebay" else "href"
        return str(a_tag[html_class])

    def build_link(self, url, page_title):
        """
        Build link from given url, adding a prefix depending on page
        @param url: url from of search result
        @param page_title: title of page search result belongs to, eg.: ebay; is set on class initialization
        @returns: full website link
        """
        prefix = str()
        prefix = "https://www.immonet.de" if page_title == "immonet" else prefix
        prefix = "https://www.ebay-kleinanzeigen.de" if page_title == "ebay" else prefix
        prefix = "https://www.immobilo.de" if page_title == "immobilo" else prefix
        return f"{prefix}{url}"

    def save_items(self):
        """save items to json file and eliminate duplicates beforehand"""
        data = read_json_file(file_path = LIST)

        blacklist = data["blacklist"]
        whitelist = data["whitelist"]

        whitelist += self.scraper_data.get_found_items()

        whitelist = self.eliminate_duplicates(list_ = whitelist)
        whitelist = self.subtract_lists(whitelist, blacklist)

        data["whitelist"] = whitelist

        write_json_file(file_path = LIST, json_object = data)

    def eliminate_duplicates(self, list_):
        """take out duplicates from given list"""
        return list(set(list_))

    def subtract_lists(self, list_a, list_b):
        "return subtraction of two lists"
        return list(set(list_a) - set(list_b))

    def no_valid_city(self, tag):
        """returns True if no valid city was found in given text, otherwise False"""
        text = str(tag)
        return True if not any(city in text for city in CITIES) else False 

def remove_from_whitelist(item):
    """remove item from whitelist"""
    data = read_json_file(file_path = LIST)

    # remove from whitelist
    whitelist = data["whitelist"]
    whitelist.remove(item)
    data["whitelist"] = whitelist

    write_json_file(file_path = LIST, json_object = data)

def add_to_blacklist(item):
    """add item to blacklist"""
    data = read_json_file(file_path = LIST)

    # add to blacklist
    blacklist = data["blacklist"]
    blacklist.append(item) 
    data["blacklist"] = blacklist

    write_json_file(file_path = LIST, json_object = data)

def create_list_of_scraper_data_objects():
    """
    Reads data from website.json and creates list of ScraperData Object from read data
    @returns: list of ScraperData objects
    """
    data = read_json_file(file_path = WEBSITE)
    scraper_data_objects = list()

    for key in data.keys():
        urls = data[key]["urls"]
        html_class = data[key]["html_class"]
        page_title = data[key]["page_title"]
        html_tag = data[key]["html_tag"]
        scraper_data_objects.append(ScraperData(urls = urls, html_class = html_class, page_title = page_title, html_tag = html_tag))

    return scraper_data_objects

if __name__=="__main__":

    data_objects = create_list_of_scraper_data_objects()

    for obj in data_objects:
        scraper = WebScraper(scraper_object = obj)
        scraper.scrape()
