from asyncore import dispatcher
import scrapy
from urllib.parse import urlparse
import html2text
import pandas as pd
import re
from bs4 import BeautifulSoup
from scrapy import Request
import signal
import os

class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = [
        "detik.com",
        # "kompas.com",
        # "tribunnews.com"
    ]
    start_urls = [
        # "https://www.detik.com/search/searchall?query=gempa&siteid=2&sortby=time&page=1",
        # "https://www.detik.com/search/searchall?query=tsunami&siteid=2&sortby=time&page=1",
        # "https://www.detik.com/search/searchall?query=puting+beliung&siteid=2&sortby=time&page=1",
        # "https://www.detik.com/search/searchall?query=gunung+meletus&siteid=2&sortby=time&page=1", ##bermasalah
        # "https://www.detik.com/search/searchall?query=kebakaran&siteid=2&sortby=time&page=1",
        # "https://www.detik.com/search/searchall?query=banjir&siteid=2&sortby=time&page=1",
        # "https://www.detik.com/search/searchall?query=abrasi&siteid=2&sortby=time&page=1",
        # "https://www.detik.com/search/searchall?query=bencana+kekeringan+air&siteid=2&sortby=time&page=1", ##bermasalah
        # "https://www.detik.com/search/searchall?query=tanah+longsor&siteid=2&sortby=time&page=1",
        "https://www.detik.com/tag/prabowo-subianto/?sortby=time&page=1"
    ]

    headers = {
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    interator = 0
    current_domain = ""
    current_subdomain = ""
    current_url = ""
    berita = []
    visited = []
    skipped_subdomain = ["travel", "20", "inet", "foto", "food"]
    page_number_detik = 2
    # skipped_subdomain = ["travel", "20", "finance", "inet",
    #                      "hot", "sport", "oto", "health", "food", "foto", "wolipop"]

    def __init__(self, *a, **kw):
        super(NewsSpider, self).__init__(*a, **kw)
        # dispatcher.connect(self.closed, signal.Signals.closed)

    def preprocessing(self, berita):
        s = str(berita)
        s = s.replace('\n', ' ')
        s = s.replace('\r', ' ')
        tokens = [token for token in s.split(" ") if token != ""]

        T = [t for t in tokens]
        return ' '.join(T)

    def parse(self, response):
        print("masuk parse")
        parsing_url = urlparse(response.request.url)
        # if ("searchall" in parsing_url.path):
        #     try:
        #         start_url = self.start_urls.pop()
        #     except IndexError:
        #         # nothing left to do
        #         return
        #     else:
        #         meta = {'start_urls': self.start_urls}
        #         yield Request(start_url, self.parse, meta=meta)

        domain = parsing_url.netloc

        if self.current_url != response.request.url:
            self.current_url = response.request.url
            self.visited.clear()

        if (domain == "www.detik.com"):
            # print("masuk detik")
            # locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
            self.domain_detik = domain
            for article in response.css("article"):

                link = article.css("a::attr(href)").extract_first()
                # print(link)

                parsed_link = urlparse(link)
                # print(parsed_link)
                self.current_subdomain = parsed_link.hostname.split('.')[0]
                # print(self.current_subdomain)

                if (self.current_subdomain not in self.skipped_subdomain) and \
                    ("edu" not in parsed_link.path) and \
                    ("foto-news" not in parsed_link.path) and \
                    ("x" not in parsed_link.path) and \
                    ("hikmah" not in parsed_link.path) and \
                    ("dw" not in parsed_link.path) and \
                    ("budaya" not in parsed_link.path) and \
                    ("foto-news" not in parsed_link.path)and \
                    ("detikflash" not in parsed_link.path)and \
                    ("detiktv" not in parsed_link.path)and \
                    ("bbc-world" not in parsed_link.path)and \
                    ("adv-nhl-detikcom" not in parsed_link.path) and \
                    ("detikupdate" not in parsed_link.path) and \
                    ("video" not in parsed_link.path) and \
                    ("suara-pembaca" not in parsed_link.path):
                    
                    yield response.follow(link, self.parse_detik)

            #PAGING
            for navbutton in response.css("div.paging"):
                # print("masuk for")
                np = navbutton.css("img").extract()
                next_page_lastel = np[-1]
                # print("nex", next_page_lastel)
                cur_url = self.current_url
                print("CUR URL",cur_url)
                if (next_page_lastel is not None) and \
                    ("Kanan" in next_page_lastel) and \
                        (NewsSpider.page_number_detik < 51):
                    
                    print("ada nextpage")
                    next_page = cur_url + "&page=" + str(NewsSpider.page_number_detik)
                    NewsSpider.page_number_detik += 1
                    # print("ADDED CUR URL", next_page)
                    # print("PAGE NUM", NewsSpider.page_number_detik)
                    # yield response.follow(next_page, callback=self.parse)
                    yield scrapy.Request(next_page, callback=self.parse, headers=self.headers)
                else:
                    print("gaada nextpage")
                    # print("SELF START URL", self.start_urls)
                    # NewsSpider.page_number_detik = 2
                    if ("searchall" in parsing_url.path):
                        # print("stop")
                        try:
                            start_url = NewsSpider.start_urls.pop()
                            print(start_url)
                        except IndexError:
                            # nothing left to do
                            return
                        else:
                            meta = {'start_urls': self.start_urls}
                            yield Request(start_url, self.parse, meta=meta)

    def parse_detik(self, response):

        author = response.css("div.detail__author::text").extract_first()

        desc = ""

        title = response.css("h1.detail__title::text").extract_first()

        if title != None:
            date = response.css("div.detail__date::text").extract_first()
        else:
            title = response.css("h1.mt5::text").extract_first()
            date = response.css("div.date::text").extract_first()

        tempTitle = self.preprocessing(title)

        date = date
        date = date

        descBody = response.css('div.detail__body-text').extract()
        description = ((self.textParser(descBody[0]).replace("*", "") + " "))

        if description != "" and title != "" and date != "":
            data = [str(tempTitle), str(date), str(
                description)]

            self.berita.append(data)

    def closed(self, reason):
        writer = pd.DataFrame(self.berita, columns=[
                              'title', 'date', 'description'])
        writer.to_csv('result/scraping/scrapped_news_prabowonews.csv',
                      index=False, sep=',')        

    def textParser(self, text):
        # return text
        soup = BeautifulSoup(text, features='lxml')
        for table in soup.find_all("table", {'class':'linksisip'}): 
            table.decompose()
        
        for table2 in soup.find_all("table", {'class': 'pic_artikel_sisip_table'}):
            table2.decompose()

        for divTag in soup.find_all("div", {'class':'detail__body-tag'}): 
            divTag.decompose()

        for divAd in soup.find_all("div", {'class': 'paradetail'}):
            divAd.decompose()

        for divVideo in soup.find_all("div", {'class':'sisip_video_ds'}): 
            divVideo.decompose()

        for divVideo1 in soup.find_all("div", {'class':'newlist-double'}):
            divVideo1.decompose()

        for divVideo2 in soup.find_all("iframe", {"class":"video20detik_0"}):
            divVideo2.decompose()

        for pScrool in soup.find_all("p", {'id':'para_caption2'}): 
            pScrool.decompose()

        for pAdv in soup.find_all("p", {'id':'adv-caption-lead'}): 
            pAdv.decompose()

        for divDaftar in soup.find_all("div", {'id':'collapsible'}): 
            divDaftar.decompose()

        for unusedStrong in soup.find_all("strong"):
            unusedStrong.decompose()

        converter = html2text.HTML2Text()
        converter.ignore_links = True

        return converter.handle(str(soup))