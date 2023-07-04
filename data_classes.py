
class ScraperData:
    def __init__(self, urls, html_class, html_tag, page_title):
        self.urls = urls
        self.html_class = html_class
        self.http_header = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0"}
        self.found_items = list()
        self.html_tag = html_tag
        self.page_title = page_title 
    
    def get_urls(self):
        return self.urls

    def get_html_class(self):
        return self.html_class

    def get_html_tag(self):
        return self.html_tag

    def get_http_header(self):
        return self.http_header

    def get_found_items(self):
        return self.found_items

    def get_html_tag(self):
        return self.html_tag
    
    def get_page_title(self):
        return self.page_title
