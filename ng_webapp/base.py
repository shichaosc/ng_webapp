"""
Django settings for pplingo project.

Generated by 'django-admin startproject' using Django 1.9.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '^b1p*!!jfhyrydtok5%vs%h%hatssw!2*^7k^_%l!t8+m-9-e^'

PREREQ_APPS = [
    'djangocms_admin_style',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django_forms_bootstrap',
    'bootstrap3',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'rest_auth',
    'rest_auth.registration',
    'opentok',
    'tz_detect',
    'storages',
    'paypal.standard.ipn',
    'wechatpy',
    'webpack_loader',
    'django_crontab',
    'explorer',
    'sekizai',
    'treebeard',
    'djangocms_text_ckeditor',
    'filer',
    'easy_thumbnails',
    'djangocms_column',
    'djangocms_file',
    'djangocms_link',
    'djangocms_picture',
    'djangocms_style',
    'djangocms_snippet',
    'djangocms_icon',
    'djangocms_video',
    'djangocms_history',
    'djangocms_teaser',
    'djangocms_inherit',
    'meta',
    'cms',
    'menus',
    'djangocms_page_meta',
    'corsheaders',
    'djangocms_bootstrap4',
    'djangocms_bootstrap4.contrib.bootstrap4_alerts',
    'djangocms_bootstrap4.contrib.bootstrap4_badge',
    'djangocms_bootstrap4.contrib.bootstrap4_card',
    'djangocms_bootstrap4.contrib.bootstrap4_carousel',
    'djangocms_bootstrap4.contrib.bootstrap4_collapse',
    'djangocms_bootstrap4.contrib.bootstrap4_content',
    'djangocms_bootstrap4.contrib.bootstrap4_grid',
    'djangocms_bootstrap4.contrib.bootstrap4_jumbotron',
    'djangocms_bootstrap4.contrib.bootstrap4_link',
    'djangocms_bootstrap4.contrib.bootstrap4_listgroup',
    'djangocms_bootstrap4.contrib.bootstrap4_media',
    'djangocms_bootstrap4.contrib.bootstrap4_picture',
    'djangocms_bootstrap4.contrib.bootstrap4_tabs',
    'djangocms_bootstrap4.contrib.bootstrap4_utilities',
    # 'raven.contrib.django.raven_compat',   # sentry 配置
]

PROJECT_APPS = [
    'course',
    'scheduler',
    'ng_webapp',
    'finance',
    'common',
    'classroom',
    'activity',
    'tutor',
    'users',
    'student',
    'ambassador',
    'log',
    'webapp',
    'homework',
    'manage'
]

CRONJOBS = [
    ('0 4 1 * *', 'tutor.tutor_scheduler.statistical_tutor_salary'),
]

INSTALLED_APPS = PREREQ_APPS + PROJECT_APPS

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'ng_webapp.middleware.TokenAuthenticationMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tz_detect.middleware.TimezoneMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'ng_webapp.context_processors.global_settings',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'sekizai.context_processors.sekizai',
                'django.template.context_processors.static',
                'cms.context_processors.cms_settings'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader'
            ],
        },
    },
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),


    # 'DEFAULT_THROTTLE_CLASSES': (
    #     # 针对未登录(匿名)用户的限流控制类
    #     'rest_framework.throttling.AnonRateThrottle',
    #     # 针对登录(认证)用户的限流控制类
    #     'rest_framework.throttling.UserRateThrottle'
    # ),
    # 指定限流频次
    'DEFAULT_THROTTLE_RATES': {
        # 认证用户的限流频次
        'user': '1/second',
        # 匿名用户的限流频次
        'anon': '1/second',
    },

}

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'ng_webapp.serializers.UserSerializer'
}

WSGI_APPLICATION = 'ng_webapp.wsgi.application'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}



SESSION_COOKIE_AGE = 60*60*48  # 10个小时
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

EXPLORER_CONNECTIONS = {'Default': 'readonly'}

EXPLORER_DEFAULT_CONNECTION = 'readonly'

EXPLORER_PERMISSION_CHANGE = lambda u: u.has_perm('explore.can_change_query')

EXPLORER_CONNECTION_NAME = 'explorer_query'  # 查询所用用户名

TZ_DETECT_COUNTRIES = ('SG', 'CN', 'ID', 'AU', 'MY', 'VN')

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ('zh-hans', _('Chinese')),
    ('en', _('English')),
]

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = '/media/'


ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
LOGIN_REDIRECT_URL = '/man/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',

    'allauth.account.auth_backends.AuthenticationBackend',
)

EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
EMAIL_HOST_USER = 'AKIAIQKYH63Y3HELX6MQ'
EMAIL_HOST_PASSWORD = 'AnD8w4ZvnWEMwDa6tDY4DouIj9c4qo29LT4BRTkGVGuA'
EMAIL_USE_TLS = True

VIDEO_SERVICE_PROVIDER = 'AGORA.IO'

SIGNALLING_SERVICE_PROVIDER = 'AGORA.IO'

AUD = 'AUD'
BRL = 'BRL'
CAD = 'CAD'
CNY = 'CNY'
CZK = 'CZK'
DKK = 'DKK'
EUR = 'EUR'
HKD = 'HKD'
HUF = 'HUF'
ILS = 'ILS'
JPY = 'JPY'
MYR = 'MYR'
MXN = 'MXN'
NOK = 'NOK'
NZD = 'NZD'
PHP = 'PHP'
PLN = 'PLN'
GBP = 'GBP'
RUB = 'RUB'
SGD = 'SGD'
SEK = 'SEK'
CHF = 'CHF'
TWD = 'TWD'
THB = 'THB'
USD = 'USD'

CURRENCY_CHOICES = (
    (AUD, 'Australian Dollar'),
    (CAD, 'Canadian Dollar'),
    (EUR, 'Euro'),
    (HKD, 'Hong Kong Dollar'),
    (JPY, 'Japanese Yen'),
    (NZD, 'New Zealand Dollar'),
    (GBP, 'Pound Sterling'),
    (SGD, 'Singapore Dollar'),
    (USD, 'U.S. Dollar'),
)

COUNTRY_CHOICES = (
    ('CN', 'China'),
    ('US', 'United States'),
    ('SG', 'Singapore'),
    ('UK', 'United Kingdom'),
    ('AU', 'Australia'),
    ('ID', 'Indonesia'),
)

CMS_TEMPLATES = (
    ('fullwidth.html', 'Fullwidth'),
    ('sidebar_left.html', 'Sidebar Left'),
    ('sidebar_right.html', 'Sidebar Right')
)

CMS_PERMISSION = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'),)

DJANGOCMS_PICTURE_NESTING = True

DJANGOCMS_PICTURE_TEMPLATES = [
    ('background', _('Background image')),
]

DJANGOCMS_PICTURE_RATIO = 1.618

COLUMN_WIDTH_CHOICES = (
    ('10%', _("10%")),
    ('25%', _("25%")),
    ('33.33%', _('33%')),
    ('50%', _("50%")),
    ('66.66%', _('66%')),
    ('75%', _("75%")),
    ('100%', _('100%')),
)

DJANGOCMS_BOOTSTRAP4_TAG_CHOICES = ['div', 'section', 'article', 'header', 'footer', 'aside']

DJANGOCMS_BOOTSTRAP4_CAROUSEL_TEMPLATES = (
    ('default', _('Default')),
)

DJANGOCMS_BOOTSTRAP4_GRID_SIZE = 12
DJANGOCMS_BOOTSTRAP4_GRID_CONTAINERS = (
    ('container', _('Container')),
    ('container-fluid', _('Fluid container')),
)
DJANGOCMS_BOOTSTRAP4_GRID_COLUMN_CHOICES = (
    ('col', _('Column')),
    ('w-100', _('Break')),
    ('', _('Empty'))
)

DJANGOCMS_BOOTSTRAP4_USE_ICONS = True

DJANGOCMS_BOOTSTRAP4_TAB_TEMPLATES = (
    ('default', _('Default')),
)

DJANGOCMS_BOOTSTRAP4_SPACER_SIZES = (
    ('0', '* 0'),
    ('1', '* .25'),
    ('2', '* .5'),
    ('3', '* 1'),
    ('4', '* 1.5'),
    ('5', '* 3'),
)

DJANGOCMS_BOOTSTRAP4_CAROUSEL_ASPECT_RATIOS = (
    (16, 9),
)
DJANGOCMS_BOOTSTRAP4_COLOR_STYLE_CHOICES = (
    ('primary', _('Primary')),
    ('secondary', _('Secondary')),
    ('success', _('Success')),
    ('danger', _('Danger')),
    ('warning', _('Warning')),
    ('info', _('Info')),
    ('light', _('Light')),
    ('dark', _('Dark')),
    ('custom', _('Custom')),
)

CMS_PAGE_CACHE = False
META_SITE_PROTOCOL = 'https'
META_SITE_DOMAIN = True

OLD_PASSWORD_FIELD_ENABLED = True
LOGOUT_ON_PASSWORD_CHANGE = False

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    '*'
)
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

DJORM_POOL_OPTIONS = {
    "pool_size": 20,
    "max_overflow": 0,
    "recycle": 3600, # the default value
}

REDIS_CONFIG = {
    'port': 6379,
    'host': '127.0.0.1'
}


DATABASE_ROUTERS = ['ng_webapp.database_router.DatabaseAppsRouter']

DATABASE_APPS_MAPPING = {
    # example:
    # 'app_name':'database_name',
    'course': 'lingoace',
    'finance': 'lingoace',
    'classroom': 'lingoace',
    'common': 'lingoace',
    'scheduler': 'lingoace',
    'tutor': 'lingoace',
    'activity': 'lingoace',
    'student': 'lingoace',
    'ambassador': 'lingoace',
    'webapp': 'pplingodb',
    'homework': 'lingoace',
    'manage': 'lingoace'
    # 'explorer': 'lingoace'
}

SITE_ID = 1

# 更新课件
UPLOAD_COURSEWARE_URL = '/danger/api/upload/uploadCourseware'

# 上传文件
UPLOAD_FILE_URL = '/danger/api/upload/uploadFile'

# 更改用户密码
UPDATE_USER_PASSWORD = '/danger/modify/password/{user_id}/{role}'

# 更新学生级别
UPDATE_STUDENT_LESSON = '/danger/api/tutor/adjust/student/edition/level/{student_user_id}/{new_edition_id}/{new_level}/{new_lesson_no}'

# 更新班级级别
UPDATE_COURSE_LEVEL = '/danger/api/tutor/adjust/smallclass/edition/level/{class_id}/{new_edition}/{new_level}/{new_lesson_no}'

# 结束课程
FINISH_VIRTUALCLASS = '/danger/api/stop/{virtualclass_id}/{tutor_user_id}'

# 获取ip真实地址
IP_AREA_URL = 'http://ip.taobao.com/service/getIpInfo2.php'

# 新浪获取真实ip地址
NEW_IP_AREA_URL = 'http://ip-api.com/batch'

# 单元报告审核
UNIT_REPORT_AUDIT_URL = '/danger/api/unitCourseReport/audit'

# 首课反馈审核
FIRST_REPORT_AUDIT_URL = '/danger/api/firstReportResult/audit'

# 成员退出班级  delete
STUDNT_SIGN_OUT_CLASS = '/danger/api/classroom/classmember/{class_id}/{student_user_id}'

# 新成员加入班级  post
STUDENT_ADD_CLASS = '/danger/api/classroom/classmember'

# 班级预约, 取消老师的时间  post
SCHEDULE_SUBSCRIBE = '/danger/api/schedule/class/subscribe'

# 更换老师
SCHEDULE_CHANGE_TUTOR = '/danger/api/schedule/class/change/tutor'

# 老师的课表
TUTOR_TIME_TABLE = '/danger/api/schedule/tutor/timetable/{tutor_user_id}/{start_time}/{end_time}'

# 学生的常用老师列表
STUDENT_OFTEN_TUTOR = '/danger/api/schedule/tutor/frequent/{student_user_id}/{class_type_id}/{page}/{page_size}'

# 符合学生条件的老师列表
STUDENT_ABLE_TUTOR = '/danger/api/schedule/tutor/eligible/{student_user_id}/{class_type_id}/{page}/{page_size}'

# 学生课表
STUDENT_TIMETABLE = '/danger/api/schedule/student/timetable/{student_user_id}/{start_time}/{end_time}'

# 学生约课 post
STUDENT_APPOINTMENT = '/danger/api/schedule/student/subscribe'

# 修改预约的老师
CHANGE_APPOINTMENTED_TUTOR = '/danger/api/schedule/change/tutor/{tutor_user_id}/{absent_tutor_user_id}/{start_time}'

# 学生批量加入班级 post
STUDENT_JOIN_CLASS = '/danger/api/user/batchStudent/joinClass'

# 百家云
BAIJIAYUN_DOMAIN = 'b33237658'

PARTNER_ID = 33237658

PARTNER_KEY = 'pdzn12TuyP0C02WAyqc2o/jsTp0qi4rlx8Idafm3TcwRVf/enPelMlhQFpoWpGN5JSK4HuKSeRxhaxA01nTOmqBzZs7xCGKZhXlDrgmWDQLorNOEyPdwxIqom5DLwWsN'

