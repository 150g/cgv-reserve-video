# -*- coding: utf-8 -*-
import re
import json

import scrapy
from scrapy.crawler import CrawlerProcess

class CGVSpider(scrapy.Spider):
    name = 'cgvspider'
    allowed_domains = ['www.cgv.co.kr']
    start_urls = ['http://www.cgv.co.kr/']
    getSeatList = 'http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx/GetSeatList'
    header = { 'Content-Type': 'application/json' }

    def start_requests(self):
        code = '0001'
        PlayYMD = '20190428'
        ScreenCode = '003'
        PlayNum = '6'
        StartTime = '2530'
        EndTime = '2841'
        TheaterName = 'CGV 강변'
        Cnt = '202'
        ScreenName = '3관'

        payload = json.dumps({
            'theatercode': code,
            'palyymd': PlayYMD,
            'screencode': ScreenCode,
            'playnum': PlayNum,
            'starttime': StartTime,
            'endtime': EndTime,
            'theatername': TheaterName,
            'cnt': Cnt,
            'screenname': ScreenName
        })

        with open('theaterCode.json') as json_file:
            self.theater = json.load(json_file)

        yield scrapy.FormRequest(url=self.getSeatList, method="POST", body=payload, headers=self.header, callback=self.parse)

    def parse(self, response):
        text = response.body_as_unicode()
        text = json.loads( text )['d']
        coordinates = re.findall(r"(reserved)?.{13}left:([0-9]{1,3})px; top:([0-9]{1,3})px;", text)
        coordinates = [ (reserved == 'reserved', int(left) // 4, int(top) // 4) for reserved, left, top in coordinates ]
        yield {
            #"text": text,
            "movie": coordinates
        }

process = CrawlerProcess()
process.crawl(CGVSpider)
process.start()
