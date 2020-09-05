from django.core.management.base import BaseCommand
from student.models import UserParentInfo
from django.db.models import Q
from finance.models import BalanceChange


all_parent_names = ['lovekenny','charles8','chloe6','huangyuxiao','catherineS','EthanB','zane','ella2008','emma2008','申澳','alice2019','amber','alex','jackie','xutiantian','sophia','jenny8','陈梓昊','冷颐轩','林姝含','gabriel+daniel','aprilyanbai','吉永光希','高金辰','赵怡媛','jiajiababy','湲湲','李正炫','甄梓行','曲嘉屹','趙欣','王禹卓','胡乐婷','Jeffery','张艺洋','伊恒','EdwardHuang','Ethan_xyz','zhuyunxin','zhuliya','nora082024','sofia','Ivy(孫卓藍)','蔡博瑞','蔡博熙','Mia','裴艺璘','candace','张浩天','larissa','赵婉彤','赵婉廷','胡冰濡','audreywang','zhaoshuying','文湛','ziwawa','liuyixin666','jaden001','Elva','Jdragonflyj@hotmail.com','yangyiyi','avonice82@hotmail.com','kailuoLin','Jakelu','Justinlu','tangwei_USA@hotmail.com','王蕾诗','祝鹤','仇天好','唐周怡','owen777','qiao777','王馨悦','mina01','chengqing666','layla-zoe','ivyli','leo66','feng8837','SkylarLin','wenjing.chen0926@gmail.com','xuhe7','刘问然666','"Etienne','"','yingchen93@gmail.com','宏宏','Danny1','Ellie1','Jacky-1','Daniel-1','JackChen','EvanZhang','christina_0111@hotmail.com','陈稳','Haoxiaoxue1221@hotmail.com','Felix9','Alicezheng','karrie2016@yahoo.com','Alex666','zlctu@foxmail.com','art','4168371767','ChloeDonohue','AlexisHruska','JennaLin','Violet21','chenyi','车骏尧','陈梓逸','Ann','KennethChen','lynnhuang','Vincent','小蘑菇','CarolHou','Athena','99greenbriar','林若鑫','倪凯文','李圳洋','liy617811','Billwang','estheewang','jay','jam81','洪珊','najia','daisycjy，Aiden_1','李启葳','黄子娴','Isabella','Cynthiayang，Priscilla','郑长睿','刘明俊','Yukai','李帛润','曹子彦','钟和乐','陈昕玥','EmilyCollins','lynnlzhang525@gmail.com','18963061666','6.30918E+12','Yilia','Yoyo-1','xu_chengyuan','叶艺淇','Adrianne和Valentina','Maggie_1','MarkWang','Lan','TristanChengcheng','JodyChen','CodyChen','颖子','吴东霖','Racheltax2018@gmail.com','蒋隽文','梁黛伊','19375102009','沈诗文','蒋钧','蒋帅','蒋文浩','何锦霖','何锦煜','芯妤','liuzhuoni','VincentWang','12253052227','江亦文','钟棋','Hongzhang','HongTruong','William鲍','陶陶','koinyemen@gmail.com','林若心','林若琰','Jingjing82516@163.com','Lynn9','jli051237105@gmail.com']


class Command(BaseCommand):

    def handle(self, *args, **options):

        for parent_name in all_parent_names:

            parent_user = UserParentInfo.objects.filter(Q(username=parent_name)|Q(email=parent_name)|Q(phone=parent_name)).first()

            if not parent_user:
                print('not found {}'.format(parent_name))
                continue
            balance_change = BalanceChange()

            balance_change.role = BalanceChange.PARENT
            balance_change.user_id = parent_user.id
            balance_change.reason = BalanceChange.COMPENSATION
            balance_change.amount = 1
            balance_change.reference = 0
            balance_change.normal_amount = 0
            balance_change.parent_user_id = parent_user.id
            balance_change.save()
