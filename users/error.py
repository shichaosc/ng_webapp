

class PhoneException(Exception):

    def __init__(self, code, error, data):
        self.code = code
        self.error = error
        self.data = data


class EmailException(Exception):

    def __init__(self, code, error, data):
        self.code = code
        self.error = error
        self.data = data


# try:
#     if not 1 < 0:
#         raise MyException(1001, '你的说法错误', '1不小于0')
# except MyException as e:
#     pass