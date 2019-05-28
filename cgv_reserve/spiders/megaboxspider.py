# -*- coding: utf-8 -*-
# need to make interval
# if you just dismiss it, your ip will be banned
import re
import json
import numpy as np
import db

import scrapy
from scrapy.crawler import CrawlerProcess

class MegaboxSpider(scrapy.Spider):
    type         = 1
    name         = 'megaboxspider'
    theaterUrl   = 'http://image2.megabox.co.kr/mop/base/footer_theater.html'
    timetableUrl = 'http://www.megabox.co.kr/pages/theater/Theater_Schedule.jsp'
    seatListUrl  = 'http://www.megabox.co.kr/DataProvider'

    def start_requests(self):
        self.db = db.DB()
        yield scrapy.Request(url=self.theaterUrl, callback=self.setTheater)
        #yield scrapy.Request(url=self.theaterUrl, callback=self.getTimetable)
        #yield scrapy.Request(url=self.theaterUrl, callback=self.getTheater)

    def setTheater(self, response):
        theaters = response.css('.wrap a')
        self.db.setTheater(theaters, self.type)

        """
        conn = sqlite3.connect("test.db")
        cur = conn.cursor()
        sql = "insert into Theater values(:name, :code, :type)"

        theater = list(map(
            lambda t: cur.execute(sql, {
                'name': t.css('::text').get(),
                'code': t.attrib['onclick'].split('cinema=')[1].split('\'')[0],
                'type': self.type
            }),
            response.css('.wrap a')
        ))
        conn.commit()
        conn.close()
        """
        """
        #for t in theater:
        yield scrapy.Request(
            url='%s?%s=%s' % ( self.timetableUrl, 'cinema', t['code'] ),
            callback=self.getTimetable
        )
        break
        """

    def getTimetable(self, response):
        conn = sqlite3.connect("test.db")
        cur = conn.cursor()
        sql = "select code from theater where type is 1"
        cur.execute(sql);
        codes = cur.fetchall()
        for code in codes:
            yield scrapy.Request(
                url='%s?%s=%s' % ( self.timetableUrl, 'cinema', code ),
                callback=self.getTimetable
            )
            break
        conn.close()
        """
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
            }
            yield scrapy.FormRequest(
                url=self.seatListUrl,
                formdata=formdata,
                meta=formdata,
                callback=self.getSeats
            )
            break
        """

    def getSeats(self, response):
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
