from django.conf.urls import url, include

from users import views as user_views
from rest_framework import routers
from users.views import LoginView, LogOutView


urlpatterns = [
    # url(r'^role/list', user_views.RoleListView.as_view(), name='role_list'),
    url(r'^login/', LoginView.as_view(), name='manager_login'),
    url(r'^logout/', LogOutView.as_view(), name='manager_logout'),
]