# -*- coding: utf-8 -*-
import re
import db
import sys
import json

import scrapy
from scrapy.crawler import CrawlerProcess

class LottecinemaSpider(scrapy.Spider):
    type         = 2
    name         = 'lottecinemaspider'
    theaterUrl   = 'http://www.lottecinema.co.kr/LCHS/Contents/Cinema/Cinema-Detail.aspx'
    timetableUrl = 'http://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx'
    seatListUrl  = 'http://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx'

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
                formdata = {
                    'paramList': json.dumps({
                        "MethodName": "GetPlaySequence",
                        "channelType": "HO",
                        "osType": "",
                        "osVersion": "",
                        "playDate": "",#"2019-05-27",
                        "cinemaID": "1|1|%s" % t[0],
                        "representationMovieCode": ""
                    })
                }
                yield scrapy.FormRequest(
                    url=self.timetableUrl,
                    formdata=formdata,
                    callback=self.setTimetable
                )
        #"""##

        #"""## write Seats to DB
        elif args.type == '1':
            timetables = self.db.getTimetable()
            f = {
                "MethodName": "GetSeats",
                "channelType": "HO",
                "osType": "",
                "osVersion": ""
            }
            for t in timetables:
                f['cinemaId'] = t[0]
                f['screenId'] = t[1]
                f['playDate'] = t[2]
                f['playSequence'] = t[3]
                f['screenDivisionCode'] = t[4]
                formdata = {
                    'paramList': json.dumps(f)
                }
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
        theaters = response.css('.depth  li:not(:nth-child(1)) .depth_03 a')
        theaters = list(map(
        lambda t: {
            'code': t.attrib['href'].split('cinemaID=')[1],
            'name': t.attrib['title']
        }, theaters))
        self.db.setTheater(theaters)

    def setTimetable(self, response):
        timetables = json.loads( response.body )['PlaySeqs']['Items']
        timetables = list(map(
        lambda t: {
            'cinemaCode': t['CinemaID'],
            'screenCode': t['ScreenID'],
            'playDate': t['PlayDt'],
            'showSeq': t['PlaySequence'],
            'showMovieCode': t['ScreenDivisionCode']
        }, timetables))
        self.db.setTimetable(timetables)

    def setSeat(self, response):
        seatList = json.loads( response.body )['BookingSeats']['Items']
        timetableId = response.meta['id']
        coordinates = list(map(
        lambda seat: {
            'x': int(seat['SeatColumn']),
            'y': ord(seat['SeatRow'])-64
        }, seatList))
        self.db.setSeat(timetableId, coordinates)

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(LottecinemaSpider)
    process.start()
