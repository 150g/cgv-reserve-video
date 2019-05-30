# -*- coding: utf-8 -*-
# need to make interval
# if you just dismiss it, your ip will be banned
import re
import json
import numpy as np
import db

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
        self.db = db.DB()
        """## write Theater to DB
        yield scrapy.Request(url=self.theaterUrl, callback=self.setTheater)
        #"""##

        #"""## write Timetable to DB
        theaters = self.db.getTheater(self.type)
        for t in theaters:
            yield scrapy.Request(
                url='%s?%s=%s' % ( self.timetableUrl, 'cinema', t[0] ),
                callback=self.setTimetable
            )
        #"""##

        """## write Timetable to DB
        timetables = self.db.getTimetable(self.type)
        for t in timetables:
            yield scrapy.Request(

            )
        #"""##

        #yield self.getSeats()

    def getTheater(self):
        return scrapy.Request(url=self.theaterUrl, callback=self.setTheater)

    def setTheater(self, response):
        theaters = response.css('.wrap a')
        self.db.setTheater(theaters, self.type)

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
        self.db.setTimetable(timetables, self.type)

    def getSeats(self):
        times = self.db.getTimetable()
        seatList = json.loads( response.body )['seatList']
        coordinates = np.array(list(map(
            lambda seat: [
                int(seat['seatNo']),
                int(seat['seatRow'])
            ],
            filter(
                lambda seat: seat['seatStatus'] == '50',
                seatList
            )
        )))
        #yield self.draw(coordinates)
        yield self.writeDB(coordinates)

    def draw(self, coordinates):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib import cm

        x = coordinates[:, 0]
        y = np.arange(-5, 5, 1)
        X, Y = np.meshgrid(x, y)
        Z = X*0

        fig = plt.figure()
        ax = fig.gca(projection='3d')              # 3d axes instance
        surf = ax.plot_surface(X, Y, Z,           # data values (2D Arryas)
                               rstride=2,                    # row step size
                               cstride=2,                   # column step size
                               cmap=cm.RdPu,        # colour map
                               linewidth=10,                # wireframe line width
                               antialiased=True)

        ax.view_init(elev=30,azim=70)                # elevation & angle
        ax.dist=8                                                  # distance from the plot
        plt.show()

process = CrawlerProcess()
process.crawl(MegaboxSpider)
process.start()
