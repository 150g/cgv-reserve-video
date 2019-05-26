# -*- coding: utf-8 -*-
# need to make interval
# if you just dismiss it, your ip will be banned
import re
import json

import scrapy
from scrapy.crawler import CrawlerProcess

class CGVSpider(scrapy.Spider):
    name         = 'cgvspider'
    theaterUrl   = 'http://www.cgv.co.kr/theaters/'
    timetableUrl = 'http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx/GetSeatList'
    header       = { 'Content-Type': 'application/json' }

    def start_requests(self):
        yield scrapy.Request(url=self.theaterUrl, callback=self.getTheater)

    def getTheater(self, response):
        html = response.body_as_unicode()
        dict = re.search( r"var theaterJsonData = (.*);", html ).group().split('= ')[1].split(';')[0]

        from functools import reduce
        theater = map( lambda i: i['AreaTheaterDetailList'], json.loads( dict ) )
        self.theater = reduce( lambda x, y: x + y, theater )

        for i in self.theater:
            print(i)
            self.theaterCode = i['TheaterCode']
            self.theaterName = i['TheaterName']
            yield scrapy.Request(
                url='%s?%s=%s' % ( self.timetableUrl, 'theaterCode', self.theaterCode ),
                callback=self.getTimetable
            )
            break

    def getTimetable(self, response):
        """
        from collections import defaultdict
        self.movies = defaultdict(lambda: {})

        for movie in response.css( '.sect-showtimes > ul > li' ):
            title = movie.css('strong::text').get().strip()
        """

        for time in response.css('.info-timetable a'):
            payload = json.dumps({
                'theatercode': self.theaterCode,
                'theatername': self.theaterName,
                'palyymd':     time.attrib['data-playymd'],
                'screencode':  time.attrib['data-screencode'],
                'playnum':     time.attrib['data-playnum'],
                'starttime':   time.attrib['data-playstarttime'],
                'endtime':     time.attrib['data-playendtime'],
                'cnt':         time.attrib['data-seatremaincnt'],
                'screenname':  time.attrib['data-screenkorname']
            });

            yield scrapy.FormRequest(
                url=self.timetableUrl,
                method="POST",
                body=payload,
                headers=self.header,
                callback=self.getSeats
            )
            break

    def getSeats(self, response):
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
