import sqlite3
class DB:
    def open(self):
        conn = sqlite3.connect('test.db')
        cur = conn.cursor()
        return conn, cur

    def getTheater(self, type):
        conn, cur = self.open()
        sql = "select code from theater where type is %d" % type
        cur.execute(sql)
        result = cur.fetchall()
        conn.close()
        return result

    def setTheater(self, theaters, type):
        conn, cur = self.open()
        sql = 'delete from Theater'
        cur.execute(sql)

        sql = "insert into Theater values(:name, :code, %s)" % type
        list(map(
        lambda t:
        cur.execute(sql, {
            'name': t.css('::text').get(),
            'code': t.attrib['onclick'].split('cinema=')[1].split('\'')[0]
        }), theaters
        ))
        conn.commit()
        conn.close()

    def setTimetable(self, timetables, type):
        conn, cur = self.open()
        sql = "insert into Timetable values(:cinemaCode, :screenCode, :playDate, :showSeq, :showMovieCode, %s)" % type
        list(map(
        lambda t: cur.execute(sql, t),
        timetables
        ))
        #cur.execute(sql, timetables[0])
        conn.commit()
        conn.close()
