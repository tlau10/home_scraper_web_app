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

    def __init__(self, urls, class_):
        self.urls = urls
        self.class_ = class_
        self.header = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0"}
        self.items = list()

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

class ImmoweltScraper(AbstractScraper):
    """Scraper class for immowelt"""

    def __init__(self, urls, class_):
        AbstractScraper.__init__(self, urls, class_)

    def scrape(self):
        """start scraping"""

        for url in self.urls:
            print(url)
            page = requests.get(url = url, headers = self.header)
            soup = BeautifulSoup(page.content, "html.parser")
            result = soup.find_all("a", class_ = self.class_)

            for a_tag in result:
                # skip <a> tags with wrong city
                text = str(a_tag)
                if not any(city in text for city in CITIES):
                    continue

                link = a_tag["href"]
                self.items.append(link)
                print(link)

        self.save_items()

class ImmonetScraper(AbstractScraper):
    """Scraper class for immonet"""

    def __init__(self, urls, class_):
        AbstractScraper.__init__(self, urls, class_)

    def scrape(self):
        """start scraping"""
        for url in self.urls:
            print(url)
            page = requests.get(url = url, headers = self.header)
            soup = BeautifulSoup(page.content, "html.parser")
            result = soup.find_all("div", class_ = self.class_)

            for div_tag in result:
                # skip <div> tags with wrong city
                text = str(div_tag)
                if not any(city in text for city in CITIES):
                    continue

                a_tag = div_tag.find("a")
                link = "https://www.immonet.de"+str(a_tag["href"])
                self.items.append(link)
                print(link)

        self.save_items()

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

    immowelt = ImmoweltScraper(urls = data["immowelt"]["urls"], class_ = data["immowelt"]["class"])
    immowelt.scrape()

    immonet = ImmonetScraper(urls = data["immonet"]["urls"], class_ = data["immonet"]["class"])
    immonet.scrape()
