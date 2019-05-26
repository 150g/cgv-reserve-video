# -*- coding: utf-8 -*-
# need to make interval
# if you just dismiss it, your ip will be banned
import re
import json

import scrapy
from scrapy.crawler import CrawlerProcess

class MegaboxSpider(scrapy.Spider):
    name         = 'megaboxspider'
    theaterUrl   = 'http://image2.megabox.co.kr/mop/base/footer_theater.html'
    timetableUrl = 'http://www.megabox.co.kr/pages/theater/Theater_Schedule.jsp'
    seatListUrl  = 'http://www.megabox.co.kr/DataProvider'

    def start_requests(self):
        yield scrapy.Request(url=self.theaterUrl, callback=self.getTheater)

    def getTheater(self, response):
        theater = list(map(
            lambda t: {
                'code': t.attrib['onclick'].split('cinema=')[1].split('\'')[0],
                'name': t.css('::text').get()
            },
            response.css('.wrap a')
        ))

        for t in theater:
            yield scrapy.Request(
                url='%s?%s=%s' % ( self.timetableUrl, 'cinema', t['code'] ),
                callback=self.getTimetable
            )
            break

    def getTimetable(self, response):
        for time in response.css('.cinema_time a'):
            formdata = re.findall( r"'(.*)'", time.attrib['onclick'] )
            formdata = {
                '_command': 'Booking.getBookingSeatInfo',
                'siteCode': '36',
                'cinemaCode': formdata[2],
                'screenCode': formdata[3],
                'playDate': formdata[5],
                'showSeq': formdata[7],
                'showMovieCode': formdata[0],
                'korEngGubun': '1'
            };
            yield scrapy.FormRequest(
                url=self.seatListUrl,
                formdata=formdata,
                callback=self.getSeats
            )
            break

    def getSeats(self, response):
        seatList = json.loads( response.body )['seatList']
        coordinates = list(map(
            lambda seat: {
                'reserved': seat['seatStatus'] == '50',
                'x': seat['seatNo'],
                'y': seat['seatRow']
            },
            seatList
        ))
        yield {
            "movie": coordinates
        }

process = CrawlerProcess()
process.crawl(MegaboxSpider)
process.start()
