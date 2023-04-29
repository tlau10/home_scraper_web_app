import requests
from bs4 import BeautifulSoup
from home_scraper_helper import read_json_file, write_json_file
import configparser
import re

config = configparser.ConfigParser()
config.read("home_scraper.ini")

WEBSITE = config["files"]["website"]
LIST = config["files"]["list"]
CITIES = ["Überlingen", "Meersburg", "Friedrichshafen", "Uhldingen", "Ueberlingen"]

class AbstractScraper:
    """Abstract scraper class"""

    def __init__(self, urls, class_, page_title, tag):
        self.urls = urls
        self.class_ = class_
        self.header = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0"}
        self.items = list()
        self.page_title = page_title 
        self.tag = tag

    def save_items(self):
        """save items to json file and eliminate duplicates beforehand"""
        data = read_json_file(file_path = LIST)

        blacklist = data["blacklist"]
        whitelist = data["whitelist"]

        whitelist += self.items

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

class GeneralScraper(AbstractScraper):
    """General Scraper class"""

    def __init__(self, urls, class_, page_title, tag):
        AbstractScraper.__init__(self, urls, class_, page_title, tag)

    def scrape(self):
        """start scraping"""
        for url in self.urls:
            print(url)
            page = self.make_request(request_url = url)
            tags = self.parse_html(html = page, tag=self.tag)

            for a_tag in tags:
                # skip <a> tags with wrong city
                if self.no_valid_city(tag = a_tag):
                    continue

                a_tag = a_tag.find("a") if self.page_title == "immonet" or self.page_title == "wohnungsboerse" or self.page_title == "immobilo" else a_tag
                link_url = self.extract_url(a_tag = a_tag, page_title = self.page_title)
                link = self.build_link(url = link_url, page_title = self.page_title)

                self.items.append(link)
                print(link)

        self.save_items()
    
    def make_request(self, request_url):
        """
        make http request to given url
        @param request_url: url to request html content from
        """
        return requests.get(url = request_url, headers = self.header)

    def parse_html(self, html, tag):
        """
        parse html page to find given tags
        @param html: html page
        @param tag: tags to find in html, eg.: <div>
        """
        soup = BeautifulSoup(html.content, "html.parser")
        return soup.find_all(tag, class_ = self.class_)

    def extract_url(self, a_tag, page_title):
        """
        Extract link from given a_tag by extracting specific html class, eg.: href
        @param a_tag: <a> tag from search result
        @param page_title: title of page search result belongs to, eg.: ebay; is set on class initialization
        """
        html_class = "data-href" if page_title == "ebay" else "href"
        return str(a_tag[html_class])

    def build_link(self, url, page_title):
        """
        Build link from given url, adding a prefix depending on page
        @param url: url from of search result
        @param page_title: title of page search result belongs to, eg.: ebay; is set on class initialization
        """
        prefix = str()
        prefix = "https://www.immonet.de" if page_title == "immonet" else prefix
        prefix = "https://www.ebay-kleinanzeigen.de" if page_title == "ebay" else prefix
        prefix = "https://www.immobilo.de" if page_title == "immobilo" else prefix
        return f"{prefix}{url}"

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

if __name__=="__main__":

    data = read_json_file(file_path = WEBSITE)

    immowelt = GeneralScraper(urls = data["immowelt"]["urls"], class_ = data["immowelt"]["class"], page_title = "immowelt", tag = "a")
    immowelt.scrape()

    immonet = GeneralScraper(urls = data["immonet"]["urls"], class_ = data["immonet"]["class"], page_title = "immonet", tag = "div")
    immonet.scrape()

    ebay = GeneralScraper(urls = data["ebay"]["urls"], class_ = data["ebay"]["class"], page_title = "ebay", tag = "article")
    ebay.scrape()

    wohnungsboerse = GeneralScraper(urls = data["wohnungsboerse"]["urls"], class_ = data["wohnungsboerse"]["class"], page_title = "wohnungsboerse", tag = "div")
    wohnungsboerse.scrape()

    immobilo = GeneralScraper(urls = data["immobilo"]["urls"], class_ = data["immobilo"]["class"], page_title = "immobilo", tag = "div")
    immobilo.scrape()
    