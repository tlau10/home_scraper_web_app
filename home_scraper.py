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

    def no_valid_city(self, tag):
        """returns True if no valid city was found in given text, otherwise False"""
        text = str(tag)
        return True if not any(city in text for city in CITIES) else False 

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
                if self.no_valid_city(tag = a_tag):
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
                if self.no_valid_city(tag = div_tag):
                    continue

                a_tag = div_tag.find("a")
                link = "https://www.immonet.de"+str(a_tag["href"])
                self.items.append(link)
                print(link)

        self.save_items()

class EbayScraper(AbstractScraper):
    """Scraper class for ebay"""

    def __init__(self, urls, class_):
        AbstractScraper.__init__(self, urls, class_)

    def scrape(self):
        """start scraping"""
        for url in self.urls:
            print(url)
            page = requests.get(url = url, headers = self.header)
            soup = BeautifulSoup(page.content, "html.parser")
            result = soup.find_all("article", class_ = self.class_)

            for article_tag in result:
                # skip <article> tags with wrong city
                if self.no_valid_city(tag = article_tag):
                    continue

                link = "https://www.ebay-kleinanzeigen.de"+str(article_tag["data-href"])
                self.items.append(link)
                print(link)

        self.save_items()

class WohnungsboerseScraper(AbstractScraper):
    """Scraper class for wohnungsboerse"""

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
                if self.no_valid_city(tag = div_tag):
                    continue
                
                a_tag = div_tag.find("a")
                link = str(a_tag["href"])
                self.items.append(link)
                print(link)

        self.save_items()

class ImmobiloScraper(AbstractScraper):
    """Scraper class for immobilo"""

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
                if self.no_valid_city(tag = div_tag):
                    continue
                
                a_tag = div_tag.find("a")
                link = "https://www.immobilo.de"+str(a_tag["href"])
                self.items.append(link)
                print(link)

        self.save_items()

class MeinestadtScraper(AbstractScraper):
    """Scraper class for Meinestadt"""

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
                if self.no_valid_city(tag = div_tag):
                    continue

            a_tag = div_tag.find("a")
            link = str(a_tag["href"])
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

    ebay = EbayScraper(urls = data["ebay"]["urls"], class_ = data["ebay"]["class"])
    ebay.scrape()

    wohnungsboerse = WohnungsboerseScraper(urls = data["wohnungsboerse"]["urls"], class_ = data["wohnungsboerse"]["class"])
    wohnungsboerse.scrape()

    immobilo = ImmobiloScraper(urls = data["immobilo"]["urls"], class_ = data["immobilo"]["class"])
    immobilo.scrape()

    meinestadt = MeinestadtScraper(urls = data["meinestadt"]["urls"], class_ = data["meinestadt"]["class"])
    meinestadt.scrape()