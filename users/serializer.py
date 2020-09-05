from rest_framework import serializers
# from users.models import Menu, Role, Department, CmsUser
from utils import utils


# class FourMenuSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Menu
#         fields = ('id', 'name', 'type', 'sort', 'url')
#
#
# class ThreeMenuSerializer(serializers.ModelSerializer):
#
#     children = FourMenuSerializer(many=True)
#
#     class Meta:
#         model = Menu
#         fields = ('id', 'name', 'type', 'sort', 'url', 'children')


# class SecondMenuSerializer(serializers.ModelSerializer):
#
#     children = ThreeMenuSerializer(many=True)
#
#     class Meta:
#         model = Menu
#         fields = ('id', 'name', 'type', 'sort', 'url', 'children')


# class MenuSerializer(serializers.ModelSerializer):
#     children = SecondMenuSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Menu
#         fields = ('id', 'name', 'type', 'sort', 'aParent', 'url', 'children')
#
#     def get_parent_name(self, obj):
#         if obj.aParent:
#             return obj.aParent.name


# class MenuListSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Menu
#         fields = '__all__'


# class DeptSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Department
#         fields = ('name', 'type')
#
#
# class RoleSerializer(serializers.ModelSerializer):
#
#     menu = MenuSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Role
#         fields = ('id', 'name', 'status', 'menu')


# class RoleListSerializer(serializers.ModelSerializer):
#     # department = DeptSerializer()
#     # user = UserSerializer(many=True)
#     # menu = MenuSerializer(many=True)
#     class Meta:
#         model = Role
#         fields = ('id', 'name', 'status')

#
# class UserRoleSerializer(serializers.ModelSerializer):
#
#     department = DeptSerializer()
#
#     class Meta:
#         model = Role
#         fields = ('id', 'name', 'department')


# class CmsUserSerializer(serializers.ModelSerializer):
#     create_time = serializers.SerializerMethodField()
#
#     def get_create_time(self, obj):
#         return utils.datetime_to_str(obj.create_time)
#
#     class Meta:
#         model = CmsUser
#         fields = ('id', 'username', 'realname', 'email', 'phone', 'work_address', 'is_active', 'create_time')


# class CmsUserRoleSerializer(CmsUserSerializer):
#
#     role = UserRoleSerializer(many=True)
#
#     class Meta(CmsUserSerializer.Meta):
#
#         fields =CmsUserSerializer.Meta.fields + ('role', )

