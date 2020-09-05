from webapp.models import *
from django.core.management.base import BaseCommand
from student.models import UserParentInfo
from manage.models import UserInfo as CmsUser
from django.db.models import Q


class Command(BaseCommand):

    def handle(self, *args, **options):

        parent_infos = UserParentInfo.objects.filter(Q(adviser_user_id__isnull=False)|Q(xg_user_id__isnull=False)).all()

        for parent_info in parent_infos:

            if parent_info.adviser_user_id:
                cms_user = CmsUser.objects.filter(id=parent_info.adviser_user_id).first()

                if cms_user:
                    parent_info.adviser_user_name = cms_user.realname

            if parent_info.xg_user_id:
                cms_user = CmsUser.objects.filter(id=parent_info.xg_user_id).first()

                if cms_user:
                    parent_info.xg_user_name = cms_user.realname

            parent_info.save()
