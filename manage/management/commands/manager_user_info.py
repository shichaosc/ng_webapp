from manage.models import *
from django.core.management.base import BaseCommand
from users.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):

        # roles = Role.objects.all()
        # RoleInfo.objects.all().delete()
        # order_no = 1
        #
        # for role in roles:
        #
        #     role_info = RoleInfo()
        #     role_info.id = role.id
        #     role_info.name_zh = role.name
        #     role_info.type = RoleInfo.NORMAL_MANAGER
        #     role_info.order_no = order_no
        #     role_info.save()
        #
        #     order_no = order_no + 1

        UserInfo.objects.all().delete()
        cms_users = CmsUser.objects.all()
        password = '24891a7870fa7424b7f7098bfb96ddf8c7c4168f48d177341b07f3cbc234764d'

        for cms_user in cms_users:

            user_info = UserInfo()
            user_info.id = cms_user.id
            user_info.code = ''
            user_info.username = cms_user.username
            user_info.realname = cms_user.realname
            # user_info.name_en = cms_user.realname
            # user_info.name_zh = cms_user.realname

            names = cms_user.realname.split('-')

            if len(names) > 1:
                user_info.name_en = names[0]
                user_info.name_zh = names[1]

            else:
                user_info.name_zh = cms_user.realname

            user_info.email = cms_user.email
            user_info.phone = cms_user.phone
            user_info.password = cms_user.password
            user_info.status = cms_user.is_active
            user_info.password = password
            user_info.save()
            role_ids = cms_user.role.all().values_list('id')
            ids = []

            for role_id in role_ids:
                # ids.append(role_id[0])
                user_role = UserRole()
                user_role.user = user_info
                user_role.role_id = role_id[0]
                user_role.save()

            # role_infos = RoleInfo.objects.filter(id__in=ids).all()
            # for role_info in role_infos:
            #     user_role = UserRole()
            #     user_role.user = user_info
            #     user_role.role = role_info
            #     user_role.save()

















