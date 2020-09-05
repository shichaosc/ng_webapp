from rest_framework import serializers
from manager.log.models import ManagerLog
from manager.users.serializer import CmsUserRoleSerializer
from manager.utils import utils


class ManagerLogSerializer(serializers.ModelSerializer):

    user = CmsUserRoleSerializer()

    create_time = serializers.SerializerMethodField()

    def get_create_time(self, obj):
        if obj.create_time:
            return utils.datetime_to_str(obj.create_time)

    class Meta:
        model = ManagerLog
        fields = ('user', 'operation', 'operate_type', 'operate_name', 'client_ip', 'create_time')
