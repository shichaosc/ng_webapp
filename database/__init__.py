import pymysql
from django.conf import settings

lingoace_db = settings.DATABASES.get('lingoace')


LINGOACE_HOST = lingoace_db.get('HOST')
LINGOACE_DB_NAME = lingoace_db.get('NAME')
LINGOACE_USER = lingoace_db.get('USER')
LINGOACE_PASSWORD = lingoace_db.get('PASSWORD')
LINGOACE_PORT = lingoace_db.get('PORT')


class MysqlDataBase(object):

    __single = None

    def __new__(cls, *args, **kwargs):

        if not cls.__single:
            cls.__single = super().__new__(cls)
        return cls.__single

    def __init__(self, host=LINGOACE_HOST, db=LINGOACE_DB_NAME, user=LINGOACE_USER, passwd=LINGOACE_PASSWORD, port=LINGOACE_PORT):

        self.connection = pymysql.Connect(
            host=host,
            db=db,
            user=user,
            passwd=passwd,
            port=int(port)
        )


    def query_sql(self, sql):

        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()

        return result