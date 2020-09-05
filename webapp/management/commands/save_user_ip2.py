from django.core.management.base import BaseCommand
import os
import re
from student.models import UserIp
from django.utils import timezone
from datetime import timedelta

IP_DICT = {}

'''输入日志文件名字解析文件'''

class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument('--file_path',
                            dest='file_path',
                            default='')

    def handle(self, *args, **options):

        file_path = options.get('file_path', '')

        self.re_ip(file_path)

    # def foreach_dir_path(self, path):
    #
    #     '''
    #     循环路径下所有文件
    #     :param path: 路径
    #     :return:
    #     '''
    #
    #     for root, dirs, files in os.walk(path):
    #
    #         for file_name in files:
    #             yesterday_time = timezone.now() + timedelta(days=-1)
    #             yesterday_str = yesterday_time.strftime('%Y-%m-%d')
    #             print(yesterday_str)
    #             print(file_name)
    #             if yesterday_str in file_name and 'info' in file_name:
    #             # if 'info' in file_name:
    #                 file_path = os.path.join(root, file_name)
    #                 self.re_ip(file_path)

    def re_ip(self, file_path):
        '''
        匹配出文件中的ip字符串
        :param file_path:  文件路径
        :return:
        '''
        f = open(file_path, 'r', encoding='utf-8')
        # pattern = re.compile('"ip":".*?"')
        pattern = re.compile('"method":"(.*?)","ip":"(.*?)"')
        for eachline in f:
            try:
                if not eachline:
                    continue
                result = pattern.search(eachline)
                if not result:
                    continue
                real_ip = result.group(2)
                if ',' in real_ip:
                    real_ip = real_ip.split(',')[0]
                role, username, uri = self.re_username(eachline)
                if not role or not username:
                    continue
                print('role', role, 'username', username, 'uri', uri)
                if role == '1':
                    result = self.save_user_ip(real_ip, role, username, uri)
                    print(result)
            except Exception as e:
                print('查询错误', e, eachline)
        print('script finish')
        f.close()

    def re_username(self, line):

        pattern = re.compile('"uri":"(.*?)","url":"(.*?)","username":"([0-9]+)(.*?007)(.*?)?"')
        result = pattern.search(line)
        if not result:
            print(line)
            return None, None, None
        uri = result.group(1)
        role = result.group(3)
        username = result.group(5)

        return role, username, uri

    def save_user_ip(self, real_ip, role, username, uri=''):
        user_ip = UserIp.objects.filter(username=username, role=role, real_ip=real_ip).first()

        if user_ip:
            if uri == '/api/user/login':
                user_ip.access_times = 1 + user_ip.access_times if user_ip.access_times else 1
                user_ip.save(update_fields=['access_times'])
            return 'success'

        user_ip = UserIp()
        user_ip.real_ip = real_ip
        user_ip.role = role
        user_ip.username = username
        user_ip.access_times = 1
        user_ip.save()
        return 'success'
