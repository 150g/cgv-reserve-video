# -*- coding: utf-8 -*-
import re
import db
import sys
import json

import scrapy
from scrapy.crawler import CrawlerProcess

class MegaboxSpider(scrapy.Spider):
    type         = 1
    name         = 'megaboxspider'
    theaterUrl   = 'http://image2.megabox.co.kr/mop/base/footer_theater.html'
    timetableUrl = 'http://www.megabox.co.kr/pages/theater/Theater_Schedule.jsp'
    seatListUrl  = 'http://www.megabox.co.kr/DataProvider'

    def start_requests(self):
        self.db = db.DB(self.type)

        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-t', '--type')
        args = parser.parse_args()

        #"""## write Theater to DB
        if args.type == '0':
            yield scrapy.Request(url=self.theaterUrl, callback=self.setTheater)
            theaters = self.db.getTheater()
            for t in theaters:
                yield scrapy.Request(
                    url='%s?%s=%s' % ( self.timetableUrl, 'cinema', t[0] ),
                    callback=self.setTimetable
                )
        #"""##

        #"""## write Seats to DB
        elif args.type == '1':
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

        #"""## draw seat from DB
        elif args.type == '2':
            import numpy as np
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            from matplotlib import cm

            coordinates = np.rot90(self.db.getSeat(), 3)
            x,y,z = coordinates

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            ax.scatter(x, y, z)
            ax.set_xlabel('X Label')
            ax.set_ylabel('Y Label')
            ax.set_zlabel('Z Label')
            ax.set_zlim(0, 50)
            plt.show()

    def setTheater(self, response):
        theaters = response.css('.wrap a')
        theaters = list(map(
        lambda t: {
            'name': t.css('::text').get(),
            'code': re.findall( r"cinema=(.*)'", t.attrib['onclick'] )[0]
        }, theaters))
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

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(MegaboxSpider)
    process.start()
