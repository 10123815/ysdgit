import MySQLdb
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class Db(object):
    
    def _connect(self):
        conn = MySQLdb.connect(db = "ysd")
        cur = conn.cursor()
        conn.set_character_set('utf8')
        cur.execute('SET NAMES utf8;') 
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')
        return conn, cur
    
    def _close(self, conn, cur):
        cur.close()
        conn.commit()
        conn.close()
        
    def _getColname(self, cur, tablename):
        sql = "select column_name from information_schema.columns where table_name = \'" + tablename + "\' and table_schema = \'ysd\'" 
        cur.execute(sql)
        colnames = [ name[0] for name in cur.fetchall() ]
        return colnames
    
    def _getResults(self, originDatas, colnames):
        results = []
        i = 0
        for dataT in originDatas:
            result = {}
            for data in dataT:
                result[colnames[i]] = data
                i += 1
            i = 0
            results.append(result)
        return results
            
    def insert(self, tablename = 'userinfo', *arg):
        conn, cur = self._connect()
        colnames = self._getColname(cur, tablename)
        colnames = [col for col in colnames if col != 'id']
        col = "(" + ", ".join(colnames) + ")"
        plc = "(" + ", ".join(["%s" for i in range(len(colnames)) ]) + ")"
        sql = "insert into %s %s values %s" % (tablename, col, plc)
        values = tuple([value for value in arg])
        cur.execute(sql, values)
        self._close(conn, cur)
        
    def selectAll(self, tablename):
        conn, cur = self._connect()
        colnames = self._getColname(cur, tablename)
        if "id" not in colnames:
            sql = "select * from %s" % tablename
            cur.execute(sql)
            results = self._getResults(cur.fetchall(), colnames) 
            self._close(conn, cur)
            return results
        colnames = [col for col in colnames if col != 'id']
        
        
    def selectCol(self, colname, tablename):
        conn, cur = self._connect()
        colnames = self._getColname(cur, tablename)
        colnames = [col for col in colnames if col != 'id']
        if colname not in colnames:
            return None
        sql = "select %s from %s" % (colname, tablename)
        cur.execute(sql)
        results = [value[0] for value in cur.fetchall()]
        self._close(conn, cur)
        return results
        
    def selectWhere(self, tablename, key, value):
        conn, cur = self._connect()
        colnames = self._getColname(cur, tablename)
        sql = "select * from %s where %s = \'%s\'" % (tablename, key, value)
        if not cur.execute(sql):
            return None
        results = self._getResults(cur.fetchall(), colnames) 
        self._close(conn, cur)
        return results
    
    def selectWhatWhere(self, tablename, what, key, value):
        conn, cur = self._connect()
        colnames = self._getColname(cur, tablename)
        for col in what:
            if col not in colnames:
                return None
        cols = ",".join(what)
        sql = "select %s from %s where %s = \'%s\'" % (cols, tablename, key, value)
        if not cur.execute(sql):
            return None
        results = self._getResults(cur.fetchall(), what) 
        self._close(conn, cur)
        return results
        
    
    def updateWhatWhere(self, tablename, what, value1, where, value2):
        conn, cur = self._connect()
        sql = "update %s set %s = \'%s\' where %s = \'%s\'" % (tablename, what, value1, where, value2)
        cur.execute(sql)
        self._close(conn, cur)
    
    def delete(self, tablename, where, value):
        conn, cur = self._connect()
        sql = "delete from %s where %s = \'%s\'" % (tablename, where, value)
        cur.execute(sql)
        self._close(conn, cur)

# d = Db()
# d.selectWhatWhere("blog", ["title", "date"], "userid", "ysd")
