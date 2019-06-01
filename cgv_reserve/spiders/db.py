import sqlite3
class DB:
    def __init__(self, type):
        self.type = type

    def open(self):
        conn = sqlite3.connect('test.db')
        cur = conn.cursor()
        return conn, cur

    def getTheater(self):
        conn, cur = self.open()
        sql = "select code from theater where type is %d" % self.type
        cur.execute(sql)
        result = cur.fetchall()
        conn.close()
        return result

    def setTheater(self, theaters):
        conn, cur = self.open()
        sql = 'delete from Theater'
        cur.execute(sql)

        sql = "insert into Theater values(:name, :code, %s)" % self.type
        list(map(
        lambda t:
        cur.execute(sql, {
            'name': t.css('::text').get(),
            'code': t.attrib['onclick'].split('cinema=')[1].split('\'')[0]
        }), theaters
        ))
        conn.commit()
        conn.close()

    def getTimetable(self):
        conn, cur = self.open()
        sql = "select * from Timetable where type=%d and playDate >= date('now')" % self.type
        cur.execute(sql)
        result = cur.fetchall()
        conn.close()
        return result

    def setTimetable(self, timetables):
        conn, cur = self.open()
        sql = "insert into Timetable values(:cinemaCode, :screenCode, :playDate, :showSeq, :showMovieCode, %s, (SELECT IFNULL(MAX(id), 0) + 1 FROM Timetable), julianday(current_timestamp))" % (self.type)
        for t in timetables:
            try: cur.execute(sql, t)
            except Exception as err:
                pass
                #print(err)
        conn.commit()
        conn.close()

    def getSeat(self):
        conn, cur = self.open()
        sql = "select s.x, s.y, (s.reservedTime-t.reservedTime) / (julianday('now')-t.reservedTime) * 100 from timetable as t, seat as s where s.timetableId = t.id and s.timetableId = 120;"
        cur.execute(sql)
        result = cur.fetchall()
        conn.close()
        return result

    def setSeat(self, id, coordinates):
        conn, cur = self.open()
        sql = "insert into Seat values(%d, julianday(current_timestamp), :x, :y)" % id
        for xy in coordinates:
            try: cur.execute(sql, xy)
            except Exception as err:
                pass
                #print(err, id, xy)
        conn.commit()
        conn.close()
