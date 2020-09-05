from student.models import UserStudentInfo, UserParentInfo
from django.db.utils import IntegrityError
from course.models import CourseQuestionnaireResult, CourseAssessmentResult
from tutor.models import TutorInfo, UserLevel
from scheduler.models import ScheduleTutorCourse, ScheduleTutorClasstype, ScheduleTutorLevel
from course.models import CourseExtcourseOwner
from webapp.models import *
from classroom.models import CourseLesson
from tutor.models import TutorInfo
import random
from student.models import UserStudentInfo
from finance.models import BalanceChangeNew as BalanceChange, RechargeOrder
from webapp.app_settings import START_ID, END_ID


def get_next_session(session):
    try:
        next_session = Session.objects.get(course=session.course, session_no=session.session_no + 1, status='Active')
    except Session.DoesNotExist:
        try:
            course = Course.objects.get(programme=session.course.programme,
                                        course_level=session.course.course_level + 1)
            next_session = Session.objects.filter(course=course, session_no=1, status='Active').first()
        except Course.DoesNotExist:
            return None
    return next_session


class CreateModel(object):

    def __init__(self, obj=None):
        self.start_id = START_ID
        self.end_id = END_ID
        self.obj = obj


class CreateStudent(CreateModel):

    def add_studen_parent_question_result(self, user: User, student: UserStudentInfo):
        '''
        家长问卷结果
        :param user:
        :param student:
        :return:
        '''
        if not student.course_edition_id:
            return
        parent_results = QuestionnaireResult.objects.filter(user=user).all()
        for parent_result in parent_results:
            course_question_result = CourseQuestionnaireResult()
            course_question_result.id = parent_result.id
            course_question_result.student_user = student
            course_question_result.result = parent_result.result
            course_question_result.result = parent_result.result
            course_question_result.edition = student.course_edition_id
            course_question_result.level = student.course_level
            course_question_result.create_time = parent_result.created_on
            course_question_result.update_time = parent_result.updated_on
            course_question_result.save()

    def add_student_assessment_result(self, user: User, student: UserStudentInfo):
        '''
        水平测试结果
        :param user:
        :param student:
        :return:
        '''
        if not student.course:
            return
        test_results = AssessmentResult.objects.filter(user=user).all()
        for test_result in test_results:
            assessment_result = CourseAssessmentResult()
            assessment_result.id = test_result.id
            assessment_result.student_user = student
            assessment_result.course = student.course
            assessment_result.pre_course = student.course
            assessment_result.detail = test_result.detail
            assessment_result.create_time = test_result.created_on
            assessment_result.update_time = test_result.updated_on
            assessment_result.save()

    def add_parent_user(self, student: User):
        '''
        添加学生家长
        :param student:
        :return:
        '''
        id = random.randint(self.start_id, self.end_id)
        password = 'password'

        parent_info = UserParentInfo.objects.filter(username=student.username).first()
        if parent_info:
            balance = AccountBalance.objects.filter(user=student).first()
            if balance:
                parent_info.balance = balance.balance
            else:
                parent_info.balance = 0
            parent_info.save()
            return None
        parent_detail = UserDetail.objects.filter(user=student).first()
        parent_profile = UserProfile.objects.filter(user=student).first()
        balance = AccountBalance.objects.filter(user=student).first()
        ext_student = ExtStudent.objects.filter(user=student).first()
        # 城市合伙人
        reference = ReferenceData.objects.filter(user=student, custom_s1__isnull=False).filter(~Q(custom_s1='')).first()

        # 转介绍  不能添加， 用户还没有导入库
        # referer = UserReferrer.objects.filter(user=student).first()

        # 课程顾问
        course_adviser = CourseAdviserStudent.objects.filter(student=student, status=CourseAdviserStudent.ACTIVE).first()
        # 学管老师
        learn_manger = LearnManagerStudent.objects.filter(student=student, status=LearnManagerStudent.ACTIVE).first()
        try:
            parent_info = UserParentInfo()
            parent_info.id = id
            parent_info.username = student.username
            parent_info.password = password

            if reference:  #城市合伙人
                parent_info.code = reference.custom_s1
            # if referer:  # 转介绍
            #     parent_info.referrer_user_name = referer.referrer.username

            if parent_detail:
                parent_info.real_name = utils.user_realname(parent_detail.last_name, student.first_name)
                parent_info.nationality = parent_detail.nationality
                parent_info.phone = parent_detail.phone_num
                parent_info.country_of_residence = parent_detail.country_of_residence
                parent_info.currency = parent_detail.currency
            if parent_profile:
                parent_info.avatar = settings.MEDIA_URL + parent_profile.avatar
            if course_adviser:
                parent_info.adviser_user_id = course_adviser.cms_user.id
                parent_info.adviser_user_name = course_adviser.cms_user.realname
            if learn_manger:
                parent_info.xg_user_id = learn_manger.cms_user.id
                parent_info.xg_user_name = learn_manger.cms_user.realname
            if ext_student:
                parent_info.whatsapp = ext_student.whatsapp
                parent_info.wechat = ext_student.weixin

            parent_info.role = UserParentInfo.CHILDREN
            parent_info.email = student.email if student.email else None
            if balance:
                parent_info.balance = balance.balance
            else:
                parent_info.balance = 0
            parent_info.bonus_balance = 0
            parent_info.status = student.is_active
            parent_info.save()
            return parent_info
        except IntegrityError as e:
            parent_info.phone = None
            parent_info.save()
            logger.error('{} 手机号码重复，err={}'.format(parent_info.username, e))
            return parent_info
        except IntegrityError as e:
            parent_info.email = None
            parent_info.save()
            logger.error('{} email重复，err={}'.format(parent_info.username, e))
            return parent_info
        except Exception as e:
            logger.error('parent_user-------{}'.format(e))

    def update_student(self, student):
        student_info = UserStudentInfo.objects.filter(real_name=student.username).first()
        if not student_info:
            return None
        student_course_info = UserCourse.objects.filter(is_default=1, user=student).first()
        balance_change = AccountBalanceChange.objects.filter(user=student,
                                                             reason=AccountBalanceChange.AD_HOC).first()
        type = UserClassType.objects.filter(user=student).first()
        if type:
            student_info.virtualclass_type_id = utils.user_type(type.virtualclass_type)
        if balance_change:
            student_info.first_course = UserStudentInfo.NOT_FIRST_COURSE
        else:
            student_info.first_course = UserStudentInfo.FIRST_COURSE
        if student_course_info:
            student_info.course_id = student_course_info.course_id
            student_info.course_edition_id = student_course_info.course.programme_id
            student_info.course_level = student_course_info.course.course_level
            print(student_course_info.course_id, student_course_info.session_no, student_course_info.id)
            lesson = CourseLesson.objects.filter(status=CourseLesson.ACTIVE,
                                                 course_id=student_course_info.course_id,
                                                 lesson_no=student_course_info.session_no).first()
            if lesson:
                student_info.lesson = lesson
                student_info.lesson_no = lesson.lesson_no
        student_info.save()


    def add_student(self):

        if not self.obj:
            return None

        student = self.obj

        parent_user = self.add_parent_user(student)
        if not parent_user:  # 家长已经存在  更新学生等级
            student_info = self.update_student(student)
            return student_info

        # 新增学生
        id = random.randint(self.start_id, self.end_id)
        print('add student, id={}, new_id={}'.format(student.id, id))
        password = 'lingoace123'

        student_detail = UserDetail.objects.filter(user=student).first()
        student_course_info = UserCourse.objects.filter(is_default=1, user=student).first()
        balance_change = AccountBalanceChange.objects.filter(user=student,
                                                             reason=AccountBalanceChange.AD_HOC).first()
        student_info = UserStudentInfo()
        student_info.id = id
        student_info.password = password
        student_info.real_name = parent_user.username
        student_info.avatar = parent_user.avatar

        if student_detail:
            student_info.gender = utils.user_gender(student_detail.gender)
            student_info.birthday = student_detail.birthdate
        if student_course_info:
            student_info.course_id = student_course_info.course_id
            student_info.course_edition_id = student_course_info.course.programme_id
            student_info.course_level = student_course_info.course.course_level
            print(student_course_info.course_id, student_course_info.session_no, student_course_info.id)
            lesson = CourseLesson.objects.filter(status=CourseLesson.ACTIVE, course_id=student_course_info.course_id,
                                                 lesson_no=student_course_info.session_no).first()
            if lesson:
                student_info.lesson = lesson
                student_info.lesson_no = lesson.lesson_no
            student_info.assessed = utils.user_assessed(student_course_info.is_assessed)
            student_info.test_level = student_course_info.test_level

        student_info.student_parent_user = parent_user
        student_info.parent_user = parent_user

        type = UserClassType.objects.filter(user=student).first()
        if type:
            student_info.virtualclass_type_id = utils.user_type(type.virtualclass_type)
        if balance_change:
            student_info.first_course = UserStudentInfo.NOT_FIRST_COURSE
        else:
            student_info.first_course = UserStudentInfo.FIRST_COURSE
        student_info.status = student.is_active
        student_info.create_time = student.date_joined
        student_info.only_smallclass = UserStudentInfo.NOT_ONLY_SMALLCLASS
        student_info.save()
        # 添加充值记录
        self.add_student_balance_change(student, student_info)
        # 添加学生家长问卷结果:
        self.add_studen_parent_question_result(student, student_info)
        # 添加学生水平测试结果
        self.add_student_assessment_result(student, student_info)
        return student_info

    def add_student_balance_change(self, student: User, student_info: UserStudentInfo):
        '''添加学生充值记录'''
        a_b_cs = AccountBalanceChange.objects.filter(user=student, reason__in=(AccountBalanceChange.TOP_UP,
                                                                               AccountBalanceChange.BONUS,
                                                                               AccountBalanceChange.REFERRAL,
                                                                               AccountBalanceChange.REFERRAL_INCENTIVE,
                                                                               AccountBalanceChange.REDEEM))
        for a_b_c in a_b_cs:
            balance_change = BalanceChange()
            balance_change.amount = a_b_c.amount
            balance_change.role = BalanceChange.PARENT
            balance_change.user_id = student_info.parent_user.id
            balance_change.reason = a_b_c.reason
            balance_change.reference = a_b_c.reference
            course_adviser_student = CourseAdviserStudent.objects.filter(start_time__lte=a_b_c.created_on, student_id=a_b_c.user_id).order_by('-start_time').first()
            learn_manager_student = LearnManagerStudent.objects.filter(start_time__lte=a_b_c.created_on, student_id=a_b_c.user_id).order_by('-start_time').first()
            if learn_manager_student:
                balance_change.xg_user_id = learn_manager_student.cms_user.id
            if course_adviser_student:
                balance_change.adviser_user_id = course_adviser_student.cms_user.id
            balance_change.create_time = a_b_c.created_on
            balance_change.update_time = a_b_c.updated_on
            balance_change.save()

        # 添加充值订单
        self.add_sale_order(student, student_info)

    def add_sale_order(self, student: User, student_info: UserStudentInfo):
        '''添加用户充值订单'''
        sales_order = SalesOrder.objects.filter(buyer=student, status=SalesOrder.PAID).all()

        for sale_order in sales_order:
            recharge_order = RechargeOrder()
            recharge_order.order_no = sale_order.order_no
            recharge_order.parent_user = student_info.parent_user
            if sale_order.coupon:
                recharge_order.code = sale_order.coupon.code
            recharge_order.recharge_amount = sale_order.point
            recharge_order.incentive_amount = 0
            a_b_c = BalanceChange.objects.filter(reference=sale_order.order_no, reason=AccountBalanceChange.BONUS).all()
            recharge_order.total_amount = sale_order.point
            if a_b_c:
                for abc in a_b_c:
                    recharge_order.total_amount = sale_order.point + abc.amount
                    recharge_order.incentive_amount = recharge_order.incentive_amount + abc.amount

            currency = ExchangeRate.objects.filter(currency=sale_order.currency).first()

            sum_price = sale_order.point * currency.rate
            recharge_order.origin_total_price = sum_price
            recharge_order.save_price = sum_price - sale_order.amount
            recharge_order.currency_id = currency.id
            recharge_order.currency = currency.currency
            recharge_order.rate = currency.rate
            recharge_order.origin_total_price = 0
            recharge_order.total_price = sale_order.amount
            recharge_order.reference = sale_order.charge_id if sale_order.charge_id else sale_order.reference
            recharge_order.status = RechargeOrder.PAID
            recharge_order.create_time = sale_order.created_on
            recharge_order.update_time = sale_order.updated_on
            recharge_order.save()


class CreateTutor(CreateModel):

    def add_tutor(self):
        '''
        添加老师
        :return:
        '''
        if self.obj:
            tutor = self.obj
            id = random.randint(self.start_id, self.end_id)
            password = 'password'
            try:
                user = tutor.user
            except Exception as e:
                print(e)
                print('tutor_id={}'.format(tutor.id))
                user = User.objects.get(id=tutor.user_id)
            tutor_info = TutorInfo.objects.filter(username=user.username).first()
            if tutor_info:
                tutor_info.total_number_of_class = tutor.total_number_of_classes
                tutor_info.save()
                return tutor_info
            user_detail = UserDetail.objects.filter(user=user).first()
            user_profile = UserProfile.objects.filter(user=user).first()
            balance = AccountBalance.objects.filter(user=user).first()
            try:
                tutor_info = TutorInfo()
                tutor_info.id = id
                print(tutor.id, '-----', id)
                tutor_info.password = password
                tutor_info.role = TutorInfo.TEACHER
                tutor_info.username = user.username
                if user_detail:
                    tutor_info.real_name = utils.user_realname(user_detail.last_name, user_detail.first_name)
                    tutor_info.phone = user_detail.phone_num
                    tutor_info.gender = utils.user_gender(user_detail.gender)
                    tutor_info.currency = user_detail.currency
                    tutor_info.birthday = user_detail.birthdate
                if user_profile:
                    tutor_info.avatar = settings.MEDIA_URL + user_profile.avatar
                if balance:
                    tutor_info.balance = balance.balance

                tutor_info.email = user.email if user.email else None
                tutor_info.nationality = tutor.nationality
                tutor_info.country_of_residence = tutor.country_of_residence
                tutor_info.description_zh = tutor.description_zhhans
                tutor_info.description_en = tutor.description
                tutor_info.rating_le = tutor.rating_LE
                tutor_info.rating_id = tutor.rating_ID
                tutor_info.rating_ot = tutor.rating_OT
                tutor_info.rating_pk = tutor.rating_PK
                tutor_info.rating = tutor.rating
                tutor_info.total_number_of_class = tutor.total_number_of_classes
                tutor_info.teaching_start_time = datetime.datetime.strptime(str(tutor.start_of_teaching),
                                                                            '%Y-%m-%d').replace(tzinfo=pytz.UTC)
                if user.is_active and not tutor.is_activate:  # 上岗隐藏
                    tutor_info.hide = TutorInfo.HIDDEN  # 是否对学生隐藏
                    tutor_info.working = TutorInfo.WORKING
                    tutor_info.status = TutorInfo.ACTIVE
                elif user.is_active and tutor.is_activate:  # 在岗
                    tutor_info.hide = TutorInfo.DISPLAY
                    tutor_info.working = TutorInfo.WORKING
                    tutor_info.status = TutorInfo.ACTIVE
                elif not user.is_active and not tutor.is_activate:  # 下岗
                    tutor_info.hide = TutorInfo.HIDDEN
                    tutor_info.status = TutorInfo.ACTIVE
                    tutor_info.working = TutorInfo.UNWORK
                else:   # 未激活
                    tutor_info.hide = TutorInfo.HIDDEN
                    tutor_info.status = TutorInfo.NOTACTIVE
                    tutor_info.working = TutorInfo.UNWORK

                # tutor_info.working = tutor.is_activate  # 是否上岗
                # tutor_info.status = user.is_active
                tutor_info.save()
            except IntegrityError as e:
                tutor_info.phone = None
                tutor_info.save()
                logger.error('{} 手机号码重复，err={}'.format(tutor_info.username, e))
            except IntegrityError as e:
                tutor_info.email = None
                tutor_info.save()
                logger.error('{} email重复，err={}'.format(tutor_info.username, e))
            except Exception as e:
                logger.error('tutor_info-------{}'.format(e))
                return None

            # 添加老师可以教收的课程，班级类型， 老师等级
            courses = tutor.course.all()
            for course in courses:  # 可教课程
                tutor_course = ScheduleTutorCourse()
                tutor_course.tutor_user = tutor_info
                tutor_course.course_id = course.id
                tutor_course.save()
            class_types = tutor.class_type.all()
            for class_type in class_types:  # 可教班型
                tutor_class_type = ScheduleTutorClasstype()
                tutor_class_type.tutor_user = tutor_info
                tutor_class_type.class_type_id = class_type.id
                tutor_class_type.save()
            grades = TutorGrade.objects.filter(user=user).all()
            for grade in grades:
                tutor_level = ScheduleTutorLevel()
                tutor_level.tutor_user = tutor_info
                tutor_level.course_edition_id = grade.programme_id
                user_levle = UserLevel.objects.filter(grade=grade.grade.grade, role=UserLevel.TEACHER).first()
                tutor_level.user_level = user_levle
                tutor_level.save()

            # 添加course_extcourseowner
            extcourseowners = ExtCourseOwner.objects.filter(user_id=tutor.user_id).all()
            for extcourseowner in extcourseowners:
                course_ext_course_owner = CourseExtcourseOwner()
                course_ext_course_owner.tutor_user = tutor_info
                course_ext_course_owner.ext_course_id = extcourseowner.ext_course_id
                course_ext_course_owner.is_favorite = extcourseowner.is_favorite
                course_ext_course_owner.save()
            #
            # # 添加老师课酬
            # tutor_salary_list = TutorSalary.objects.filter(user=tutor.user).all()
            # for tutor_salary in tutor_salary_list:
            #     tutor_salary_new = TutorSalaryNew()
            #     tutor_salary_new.tutor_user_id = tutor_info.id
            #     tutor_salary_new.lesson_num = tutor_salary.lesson_num
            #     tutor_salary_new.delivery_salary = tutor_salary.delivery_salary
            #     tutor_salary_new.incentive_salary = tutor_salary.incentive_salary
            #     tutor_salary_new.absenc_compensation_salary = tutor_salary.absenc_compensation_salary
            #     tutor_salary_new.no_show_salary = tutor_salary.no_show_salary
            #     tutor_salary_new.student_num = tutor_salary.student_num
            #     tutor_salary_new.data_date = tutor_salary.data_date
            #     tutor_salary_new.pay_status = tutor_salary.pay_status
            #     tutor_salary_new.order_no = tutor_salary.order_no
            #     tutor_salary_new.save()
