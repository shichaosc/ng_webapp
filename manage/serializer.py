from rest_framework import serializers
from manage.models import UserInfo
from utils import utils


class UserInfoSerializer(serializers.ModelSerializer):

    create_time = serializers.SerializerMethodField()

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    class Meta:
        model = UserInfo
        fields = ('id', 'username', 'realname', 'email', 'phone', 'status', 'create_time')

