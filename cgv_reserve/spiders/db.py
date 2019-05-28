import sqlite3
class DB:
    def open(self):
        conn = sqlite3.connect('test.db')
        cur = conn.cursor()
        return conn, cur

    def getTheater(self, type):
        conn, cur = self.open()
        sql = "select code from theater where type is ?"
        cur.execute(sql, (type))
        conn.close()
        return cur.fetchall()

    def setTheater(self, theaters, type):
        conn, cur = self.open()
        sql = 'delete from Theater'
        cur.execute(sql)

        sql = "insert into Theater values(:name, :code, :type)"
        list(map(
        lambda t:
        cur.execute(sql, {
            'name': t.css('::text').get(),
            'code': t.attrib['onclick'].split('cinema=')[1].split('\'')[0],
            'type': type
        }), theaters
        ))
        conn.commit()
        conn.close()
