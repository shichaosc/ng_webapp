"""pplingo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.authtoken import views

from . import man_urls
from classroom import urls as classroom_url
from users import urls as users_url
from student import urls as student_url
from finance import urls as finance_url
from tutor import urls as tutor_url
from course import urls as course_url
from unit_report import urls as unit_report_url
from homework import urls as homework_url
from activity import urls as activity_url


urlpatterns = [

    url(r'^man/', include(man_urls)),
    url(r'^', include(classroom_url)),
    url(r'^', include(users_url)),
    url(r'^', include(student_url)),
    url(r'^', include(finance_url)),
    url(r'^', include(tutor_url)),
    url(r'^', include(course_url)),
    url(r'^', include(unit_report_url)),
    url(r'^', include(homework_url)),
    url(r'^', include(activity_url)),

    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^tz_detect/', include('tz_detect.urls')),
    url(r'^explorer/', include('explorer.urls')),

    url(r'^', include('cms.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

