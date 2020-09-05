from django.core.management.base import BaseCommand
from scheduler.models import TutorTimetable, StudentTimetable
from django.db import connections


IP_DICT = {}


class Command(BaseCommand):

    def handle(self, *args, **options):
        print("start")
        with connections['lingoace'].cursor() as cursor:

            sql = """SELECT
                usi.real_name AS student_name,  -- 0
                uti.username AS tutor_name,   -- 1
                stt.id,  -- 2
                stt.tutor_user_id,  -- 3
                stt.student_user_id,  -- 4
                stt.start_time,  -- 5
                stt.status  -- 6
            FROM
                schedule_tutor_timetable stt
                RIGHT JOIN ( SELECT tutor_user_id, start_time FROM schedule_tutor_timetable GROUP BY tutor_user_id, start_time HAVING count( * ) > 1 ) tmp ON ( stt.tutor_user_id = tmp.tutor_user_id AND stt.start_time = tmp.start_time )
                LEFT JOIN user_tutor_info uti ON stt.tutor_user_id = uti.id
                LEFT JOIN user_student_info usi ON usi.id = stt.student_user_id 
            WHERE
                stt.start_time > '2020-01-22 00:00:00' 
            ORDER BY
                stt.tutor_user_id,
                stt.start_time
                
            """
            cursor.execute(sql)
            row = cursor.fetchall()
            for i in range(len(row)-1):

                if row[i][3] == row[i+1][3] and row[i][5] == row[i+1][5]:

                    # if row[i][6] == TutorTimetable.SUCCESS_APPOINTMENT:  # 预约成功
                    self.handle_tutor_timetable(row[i][6], row[i+1][6], row[i][2], row[i+1][2])

    def handle_tutor_timetable(self, status, below_status, tutor_timetable_id, below_timetable_id):

        '''

        :param status: 老师课表状态
        :param tutor_timetable_id:  老师课表id
        :param before_timetable_id:  重复的老师课表id
        :return:
        '''
        try:
            tutor_timetable = TutorTimetable.objects.get(id=tutor_timetable_id)
            below_timetable = TutorTimetable.objects.get(id=below_timetable_id)
        except:
            return

        if status == TutorTimetable.SUCCESS_APPOINTMENT:  # 已预约

            if below_status == TutorTimetable.SUCCESS_APPOINTMENT:
                print(tutor_timetable_id, below_timetable_id, 'can not delete')

            # elif below_status == TutorTimetable.OCCUPATION:
            #     # self.student_timetable_status(below_timetable)
            #     print('delete tutor timetable, id=', below_timetable_id)
            #     TutorTimetable.objects.filter(id=below_timetable_id).delete()
            else:
                below_timetable.delete()
                print('delete below id=', below_timetable_id)

        elif status == TutorTimetable.PUBLISHED:

            if below_status == TutorTimetable.PUBLISHED:

                ''' 两个都是发布状态， 删除一个 '''
                print('delete published id=', below_timetable_id)
                below_timetable.delete()

            elif below_status == TutorTimetable.SUCCESS_APPOINTMENT:
                '''一个发布，一个已预约，删除发布的'''
                print('delete published id=', tutor_timetable_id)
                tutor_timetable.delete()

            elif below_status == TutorTimetable.OCCUPATION:
                result = self.student_timetable_status(below_timetable)
                if result:
                    print('delete published, id=', tutor_timetable_id)
                    tutor_timetable.delete()
                else:
                    print('delete occupend, id=', below_timetable_id)
                    below_timetable.delete()

            elif below_status == TutorTimetable.SUCCESS_APPOINTMENT:
                '''一个发布，一个预约，删除发布'''
                print('delete published, id=', tutor_timetable_id)
                tutor_timetable.delete()

        elif status == TutorTimetable.OCCUPATION:
            '''预占'''
            if below_status == TutorTimetable.SUCCESS_APPOINTMENT:

                tutor_timetable.delete()
                print('delete occupation id=', tutor_timetable_id)
            elif below_status == TutorTimetable.OCCUPATION:
                print('two occupation id=', tutor_timetable_id, below_timetable_id)
            else:
                print('delete below id=', below_timetable_id)
                below_timetable.delete()

    def student_timetable_status(self, tutor_timetble: TutorTimetable, delete=None):

        tutor_user_id = tutor_timetble.tutor_user_id

        start_time = tutor_timetble.start_time

        student_user_id = tutor_timetble.student_user_id

        student_timetable = StudentTimetable.objects.filter(start_time=start_time, tutor_user_id=tutor_user_id, student_user_id=student_user_id).first()

        if delete:
            # student_timetable.delete()
            print('delete student timetable, id=', student_timetable.id)
            return 0

        if student_timetable:
            return 1  # 不删除
        else:
            return 0  # 删除
