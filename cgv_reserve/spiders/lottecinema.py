# -*- coding: utf-8 -*-
# need to make interval
# if you just dismiss it, your ip will be banned
import re
import json

import scrapy
from scrapy.crawler import CrawlerProcess

class MegaboxSpider(scrapy.Spider):
    name         = 'lottecinemaspider'
    theaterUrl   = 'http://www.lottecinema.co.kr/LCHS/Contents/Cinema/Cinema-Detail.aspx'
    timetableUrl = 'http://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx'
    seatListUrl  = 'http://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx'

    def start_requests(self):
        yield scrapy.Request(url=self.theaterUrl, callback=self.getTheater)

    def getTheater(self, response):
        theater = list(map(
            lambda t: {
                'code': t.attrib['href'].split('cinemaID=')[1],
                'name': t.attrib['title']
            },
            response.css('.depth  li:not(:nth-child(1)) .depth_03 a')
        ))

        for t in theater:
            formdata = {
                'paramList': json.dumps({
                    "MethodName": "GetPlaySequence",
                    "channelType": "HO",
                    "osType": "",
                    "osVersion": "",
                    "playDate": "",#"2019-05-27",
                    "cinemaID": "1|1|%s" % t['code'],
                    "representationMovieCode": ""
                })
            }
            yield scrapy.FormRequest(
                url=self.timetableUrl,
                formdata=formdata,
                callback=self.getTimetable
            )
            break

    def getTimetable(self, response):
        for time in json.loads( response.body )['PlaySeqs']['Items']:
            formdata = {
                'paramList': json.dumps({
                    "MethodName": "GetSeats",
                    "channelType": "HO",
                    "osType": "",
                    "osVersion": "",
                    "cinemaId": time['CinemaID'],
                    "screenId": time['ScreenID'],
                    "playDate": time['PlayDt'],
                    "playSequence": time['PlaySequence'],
                    "screenDivisionCode": time['ScreenDivisionCode']
                })
            }
            yield scrapy.FormRequest(
                url=self.seatListUrl,
                formdata=formdata,
                callback=self.getSeats
            )
            break

    def getSeats(self, response):
        response = json.loads( response.body )
        seatList = response['Seats']['Items']

        reserved = list(map(
            lambda seat: seat['SeatNo'],
            response['BookingSeats']['Items']
        ))

        coordinates = list(map(
            lambda seat: {
                'reserved': seat['SeatNo'] in reserved,
                'x': seat['SeatColumn'],
                'y': seat['SeatRow']
            },
            seatList
        ))
        yield {
            "movie": coordinates
        }

process = CrawlerProcess()
process.crawl(MegaboxSpider)
process.start()
