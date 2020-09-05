from webapp.models import *
from django.core.management.base import BaseCommand
import random
from ambassador.models import UserAmbassadorInfo
from webapp import utils
from common.models import CommonAmbassadorCode
from django.db.utils import IntegrityError
from webapp.utils import print_insert_table_times

start_id = 1000000000000000
end_id = 10000000000000000


class Command(BaseCommand):

    @print_insert_table_times
    def add_ambassador(self):
        '''
        添加城市合伙人
        :return:
        '''
        ambassadors = Ambassador.objects.all()
        for ambassador in ambassadors:
            id = random.randint(start_id, end_id)
            password = 'password'
            user = ambassador.user

            ambassadors_info = UserAmbassadorInfo.objects.filter(username=user.username).first()
            if ambassadors_info:
                continue
            user_detail = UserDetail.objects.filter(user=user).first()
            user_profile = UserProfile.objects.filter(user=user).first()
            ambassador_info = UserAmbassadorInfo()
            try:
                ambassador_info.id = id
                ambassador_info.username = user.username
                ambassador_info.password = password
                ambassador_info.role = UserAmbassadorInfo.AMBASSADOR

                if user_detail:
                    ambassador_info.nationality = user_detail.nationality
                    ambassador_info.currency = user_detail.currency
                if user_profile:
                    ambassador_info.avatar = user_profile.avatar

                ambassador_info.real_name = utils.user_realname(ambassador.last_name, ambassador.first_name)
                ambassador_info.gender = utils.user_gender(ambassador.gender)
                ambassador_info.birthday = ambassador.birthdate
                ambassador_info.country_of_residence = ambassador.country_of_residence
                ambassador_info.whatsapp = ambassador.whatsapp
                ambassador_info.wechat = ambassador.wechat
                ambassador_info.occupation = ambassador.occupation
                ambassador_info.status = user.is_active
                # 城市合伙人码
                general_code = GeneralCode.objects.filter(user=user, is_used=1).first()
                if general_code:
                    ambassador_info.code = general_code.code
                else:
                    common_ambassador_code = CommonAmbassadorCode.objects.filter(is_used=CommonAmbassadorCode.NO_USE).first()
                    ambassador_info.code = common_ambassador_code.code
                if ambassador.telephone_no:
                    ambassador_info.phone = ambassador.telephone_no
                else:
                    ambassador_info.phone = None
                ambassador_info.email = user.email if user.email else None
                ambassador_info.save()
            except IntegrityError as e:
                print(e)
                ambassador_info.phone = None
                ambassador_info.save()
                logger.error('error, {} 手机号码重复，err={}'.format(ambassador.id, e))

            except IntegrityError as e:
                ambassador_info.email = None
                ambassador_info.save()
                logger.error('error, {} email重复，err={}'.format(ambassador.id, e))
            except Exception as e:
                logger.error('error, {}, ambassador-------{}'.format(ambassador.id, e))
                continue
            print("----------", ambassador.id)
            if ambassador_info.code:
                ambassador_code = CommonAmbassadorCode.objects.filter(code=ambassador_info.code).first()
                ambassador_code.ambassador_user_id = ambassador_info.id
                ambassador_code.is_used = 1
                ambassador_code.save()

    def handle(self, *args, **options):

        UserAmbassadorInfo.objects.all().delete()
        # 城市合伙人
        self.add_ambassador()










