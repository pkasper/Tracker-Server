import pymysql
import time

class DbConnector:
    db_cursor = None
    db_connection = None
    db_host = 'localhost'

    def connect(self):
        try:
            self.db_connection = pymysql.connect(host=self.db_host,
                                             port=3306,
                                             user='wikigame',
                                             passwd='wiki4schools',
                                             db='wikigame',
                                             charset='utf8')
            self.db_cursor = self.db_connection.cursor(pymysql.cursors.DictCursor)
            print("Database Connection Established")
        except pymysql.err.OperationalError as _error:
            print("SQL ERROR: " + str(_error))
            time.sleep(5)
            self.connect()

    def alivecheck(self):
        try:
            self.db_cursor.execute("SELECT 1", ())
            return True
        except pymysql.err.OperationalError as _error:
            print("SQL ERROR: " + str(_error))
            self.connect()
            time.sleep(2)
            return self.alivecheck()

    def __init__(self):
        self.connect()

    def __exit__(self):
        self.db_cursor.close()
        self.db_connection.close()

    def execute(self, _statement, _args, _type):
        if self.alivecheck():
            self.db_cursor.execute(_statement, _args)


        if _type == "SELECT":
            return self.db_cursor.fetchall()

    def commit(self):
        self.db_cursor.connection.commit()

    def fetch_cursor(self, _statement, _args):
        self.db_cursor.execute(_statement, _args)
        return self.db_cursor