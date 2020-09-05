from django.core.management.base import BaseCommand
from student.models import UserIp
import requests
from django.conf import settings
import json
from student.models import UserParentInfo
from django.utils import timezone

IP_DICT = {}

'''定时任务，查询没有地址的ip，解析'''

class Command(BaseCommand):

    def handle(self, *args, **options):

        no_parent_user_user_ips = UserIp.objects.filter(parent_user_id__isnull=True, role=1).all()[:30]

        for no_parent_user_user_ip in no_parent_user_user_ips:
            username = no_parent_user_user_ip.username
            user_parent_info = UserParentInfo.objects.filter(username=username).first()
            if user_parent_info:
                # UserIp.objects.filter(parent_user_id__isnull=True, role=1, username=username).all().update(parent_user_id=user_parent_info.id, update_time=timezone.now())
                no_parent_user_user_ip.parent_user_id = user_parent_info.id
                no_parent_user_user_ip.save(update_fields=['parent_user_id'])

        user_ips = UserIp.objects.filter(country_id__isnull=True).order_by('role').all()[:20]

        ips = []
        ips_dict = {}
        for user_ip in user_ips:
            user_parent_info = None
            other_user_ip = UserIp.objects.filter(real_ip=user_ip.real_ip, country_id__isnull=False).first()
            if user_ip.role == 1 and not user_ip.parent_user_id:
                user_parent_info = UserParentInfo.objects.filter(username=user_ip.username).first()
            if other_user_ip:
                user_ip.country = other_user_ip.country
                user_ip.country_id = other_user_ip.country_id
                user_ip.region = other_user_ip.region
                user_ip.region_id = other_user_ip.region_id
                user_ip.city_id = other_user_ip.city_id
                user_ip.city = other_user_ip.city
                user_ip.longitude = other_user_ip.longitude
                user_ip.latitude = other_user_ip.latitude
                if user_parent_info:
                    user_ip.parent_user_id = user_parent_info.id
                user_ip.save()
                continue
            ips.append(user_ip.real_ip)

            if user_parent_info:
                user_ip.parent_user_id = user_parent_info.id
                user_ip.save(update_fields=['parent_user_id'])

        ips = list(set(ips))
        if ips:
            results = self.get_ip_area(ips)
            if not results:
                return
            for res in results:
                if res.get('status', '') == 'success':
                    country_id = res.get('countryCode')
                    country = res.get('country')
                    region = res.get('regionName')
                    region_id = res.get('region')
                    # city_id = res.get('data').get('city_id')
                    city = res.get('city')
                    longitude = res.get('lon')
                    latitude = res.get('lat')
                    real_ip = res.get('query')
                    ips.remove(real_ip)
                    UserIp.objects.filter(real_ip=real_ip, country_id__isnull=True).update(country=country,
                                                                                           country_id=country_id,
                                                                                           region=region,
                                                                                           region_id=region_id,
                                                                                           city=city,
                                                                                           latitude=latitude,
                                                                                           longitude=longitude,
                                                                                           update_time=timezone.now())

        UserIp.objects.filter(real_ip__in=ips).delete()

    def get_ip_area(self, real_ips):
        try:
            param = {
                'lang': 'zh-CN'
            }
            response = requests.post(settings.NEW_IP_AREA_URL, params=param, json=real_ips)
            res = response.json()
        except Exception as e:
            print('get user ip area fial, error={}'.format(e))
            return None

        return res

        if res['status'] == 'success':
            country_id = res.get('countryCode')
            country = res.get('country')
            region = res.get('regionName')
            region_id = res.get('region')
            # city_id = res.get('data').get('city_id')
            city = res.get('city')
            longitude = res.get('lon')
            latitude = res.get('lat')

            return dict(
                country_id=country_id,
                country=country,
                region=region,
                region_id=region_id,
                # city_id=city_id,
                city=city,
                latitude=latitude,
                longitude=longitude
            )

        print('get user ip area fial', json.dumps(res))
        return None


    # def get_ip_area(self, real_ip):
    #
    #     params = {"ip": real_ip}
    #     try:
    #         response = requests.post(settings.IP_AREA_URL, params=params)
    #         res = response.json()
    #     except Exception as e:
    #         print('get user ip area fial, error={}'.format(e))
    #         return None
    #
    #     if res['code'] == 0:
    #         country_id = res.get('data').get('country_id')
    #         country = res.get('data').get('country')
    #         region = res.get('data').get('region')
    #         region_id = res.get('data').get('region_id')
    #         city_id = res.get('data').get('city_id')
    #         city = res.get('data').get('city')
    #
    #         return dict(
    #             country_id=country_id,
    #             country=country,
    #             region=region,
    #             region_id=region_id,
    #             city_id=city_id,
    #             city=city
    #         )
    #
    #     print('get user ip area fial', json.dumps(res))
    #     return None
