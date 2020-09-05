import aiomysql


class MysqlConnection(object):

    def __init__(self):
        self.conn = None
        self.pool = None

    async def init_pool(self, **kwargs):

        __pool = await aiomysql.create_pool(minsize=5,
                                            maxsize=10,
                                            host='127.0.0.1',
                                            port=3306,
                                            user='root',
                                            password='123456',
                                            db='mytest',
                                            autocommit=False)
        return __pool
