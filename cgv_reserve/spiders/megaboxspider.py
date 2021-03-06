# -*- coding: utf-8 -*-
# need to make interval
# if you just dismiss it, your ip will be banned
import re
import db
import json

import scrapy
from scrapy.crawler import CrawlerProcess

# get from server, set to db
class MegaboxSpider(scrapy.Spider):
    type         = 1
    name         = 'megaboxspider'
    theaterUrl   = 'http://image2.megabox.co.kr/mop/base/footer_theater.html'
    timetableUrl = 'http://www.megabox.co.kr/pages/theater/Theater_Schedule.jsp'
    seatListUrl  = 'http://www.megabox.co.kr/DataProvider'

    def start_requests(self):
        self.db = db.DB(self.type)
        """## write Theater to DB
        yield scrapy.Request(url=self.theaterUrl, callback=self.setTheater)
        #"""##

        """## write Timetable to DB
        theaters = self.db.getTheater()
        for t in theaters:
            yield scrapy.Request(
                url='%s?%s=%s' % ( self.timetableUrl, 'cinema', t[0] ),
                callback=self.setTimetable
            )
        #"""##

        #"""## write Seats to DB
        timetables = self.db.getTimetable()
        formdata = {
            '_command': 'Booking.getBookingSeatInfo',
            'siteCode': '36',
            'korEngGubun': '1'
        }
        for t in timetables:
            formdata['cinemaCode'] = t[0]
            formdata['screenCode'] = t[1]
            formdata['playDate'] = t[2]
            formdata['showSeq'] = t[3]
            formdata['showMovieCode'] = t[4]
            yield scrapy.FormRequest(
                url=self.seatListUrl,
                formdata=formdata,
                meta={'id': t[6]},
                callback=self.setSeat
            )
        #"""##

    def setTheater(self, response):
        theaters = response.css('.wrap a')
        self.db.setTheater(theaters)

    def setTimetable(self, response):
        timetables = map(
            lambda t: re.findall( r"'(.*)'", t.attrib['onclick'] ),
            response.css('.cinema_time a')
        )
        timetables = list(map(
        lambda f: {
            'cinemaCode': f[2],
            'screenCode': f[3],
            'playDate': f[5],
            'showSeq': f[7],
            'showMovieCode': f[0]
        }, timetables
        ))
        self.db.setTimetable(timetables)

    def setSeat(self, response):
        seatList = json.loads( response.body )['seatList']
        timetableId = response.meta['id']
        coordinates = list(map(
            lambda seat: {
                'x': int(seat['seatNo']),
                'y': ord(seat['seatGroup'])-64
            },
            filter(
                lambda seat: seat['seatStatus'] == '50',
                seatList
            )
        ))
        self.db.setSeat(timetableId, coordinates)

process = CrawlerProcess()
process.crawl(MegaboxSpider)
process.start()
