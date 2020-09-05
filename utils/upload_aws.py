from django.conf import settings
import requests
import logging

logger = logging.getLogger('pplingo.ng_webapp.course')


def upload_courseware(origin_lesson_id, lesson_id, cw_type, cw_name, req_file):
    logger.debug('lesson_id: {}, cw_name: {}, req_file: {}'.format(lesson_id, cw_name, req_file))
    params = {
        'lessonId': lesson_id,
        'originLessonId': origin_lesson_id,
        'cwType': cw_type,
        'cwName': cw_name,
    }

    files = {
        "file": req_file
    }

    upload_url = 'http://' + settings.JAVA_DOMAIN + settings.UPLOAD_COURSEWARE_URL
    logger.debug('upload url: {}'.format(upload_url))
    result = requests.post(upload_url, data=params, files=files)
    logger.debug(result)
    result = result.json()
    logger.debug('upload courseware, lesson_id={}, result={}'.format(lesson_id, result))
    if result.get('code') == 200:
        return 0
    return 1


def upload_file(category, file):
    '''
    上传文件或图片， 不做处理
    :return:
    '''
    params = {
        'category': category
    }

    files = {
        'file': file
    }

    file_path = ''

    upload_url = 'http://' + settings.JAVA_DOMAIN + settings.UPLOAD_FILE_URL

    result = requests.post(upload_url, data=params, files=files)
    result = result.json()

    if result.get('code') == 200:
        file_path = result.get('data')

    return file_path


