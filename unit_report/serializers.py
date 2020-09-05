from rest_framework import serializers
from utils import utils
from tutor.models import TutorInfo
from student.models import UserStudentInfo, UserParentInfo
from classroom.models import CourseReportFine
from classroom.models import VirtualclassUnitReport, VirtualclassUnitReportAudit, \
    VirtualclassFirstReportAudit, VirtualclassFirstReport, VirtualclassInfo
from course.models import CourseLesson
from django.utils import timezone
from manage.models import UserInfo


class ParentInfoSerializer(serializers.ModelSerializer):

    parent_name = serializers.SerializerMethodField()
    adviser_user_name = serializers.SerializerMethodField()
    xg_user_name = serializers.SerializerMethodField()

    def get_xg_user_name(self, obj):
        user_infos = self.context.get('user_infos', {})
        if user_infos:
            user_info = user_infos.get(obj.xg_user_id)
            if user_info:
                return user_info.realname
        else:
            user_info = UserInfo.objects.filter(id=obj.xg_user_id).first()
            if user_info:
                return user_info.realname

    def get_adviser_user_name(self, obj):
        user_infos = self.context.get('user_infos', {})
        if user_infos:
            user_info = user_infos.get(obj.adviser_user_id)
            if user_info:
                return user_info.realname
        else:
            user_info = UserInfo.objects.filter(id=obj.adviser_user_id).first()
            if user_info:
                return user_info.realname

    def get_parent_name(self, obj):
        return obj.username

    class Meta:
        model = UserParentInfo
        fields = ('parent_name', 'xg_user_name', 'adviser_user_name', 'country_of_residence')


class StudentInfoSerializer(serializers.ModelSerializer):

    parent_user = ParentInfoSerializer()

    class Meta:
        model = UserStudentInfo
        fields = ('id', 'real_name', 'parent_user')


class TutorInfoSerializer(serializers.ModelSerializer):

    tutor_name = serializers.SerializerMethodField()

    def get_tutor_name(self, obj):
        return obj.username

    class Meta:
        model = TutorInfo
        fields = ('tutor_name', 'phone', 'real_name', 'identity_name')


class UnitReportSerializer(serializers.ModelSerializer):

    unit = serializers.SerializerMethodField()
    student_user = StudentInfoSerializer()
    tutor_user = TutorInfoSerializer()
    first_start_time = serializers.SerializerMethodField()
    last_start_time = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()
    unit_result = serializers.SerializerMethodField()  # 审核结果
    fine_result = serializers.SerializerMethodField()  # 罚金
    remark_result = serializers.SerializerMethodField()  # 备注信息

    def get_remark_result(self, obj):
        remark = {
            'remark': '',
            'remark_name': ''
        }
        if obj.remark:
            remark['remark'] = obj.remark
        if obj.remark_user_id:
            user_infos = self.context.get('user_infos', {})
            user_info = user_infos.get(obj.remark_user_id)
            if user_info:
                remark['remark_name'] = user_info.realname
        return remark

    def get_fine_result(self, obj):
        report_fines = CourseReportFine.objects.filter(report_id=obj.id, type=CourseReportFine.UNIT_REPORT).all()
        result = []
        for report_fine in report_fines:
            user_infos = self.context.get('user_infos', {})
            user_info = user_infos.get(report_fine.user_id)
            result.append({
                'user': user_info.realname if user_info else '',
                'create_time': report_fine.create_time,
                'money': report_fine.money,
                'remark': report_fine.remark
            })
        return result

    def get_unit_result(self, obj):

        report_result = obj.unit_report_audit.first()

        # report_result = VirtualclassUnitReportAudit.objects.filter(unit_report_id=obj.id).first()
        if report_result:
            user_infos = self.context.get('user_infos', {})
            user_info = user_infos.get(report_result.audit_user_id)
            return {
                'examine_time': utils.datetime_to_str(report_result.create_time),
                'examiner': user_info.realname if user_info else '',
            }

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    def get_first_start_time(self, obj):
        if obj.first_start_time:
            return utils.datetime_to_str(obj.first_start_time)

    def get_last_start_time(self, obj):
        if obj.last_start_time:
            return utils.datetime_to_str(obj.last_start_time)

    def get_unit(self, obj):

        virtualclass = obj.virtual_class
        if virtualclass:
            return {
                'course_edition': virtualclass.lesson.course.course_edition_id,
                'course_level': virtualclass.lesson.course.course_level,
                'lesson_no': virtualclass.lesson_no,
                'unit': obj.unit_no
            }

    class Meta:
        model = VirtualclassUnitReport
        fields = ('id', 'student_user', 'tutor_user', 'unit', 'submit_count', 'first_start_time', 'last_start_time', 'create_time', 'status', 'unit_result', 'read_status', 'fine_result', 'remark_result')


class UnitReportDetailSerializer(serializers.ModelSerializer):

    unit = serializers.SerializerMethodField()
    student_user = StudentInfoSerializer()
    tutor_user = TutorInfoSerializer()
    # first_start_time = serializers.SerializerMethodField()
    # last_start_time = serializers.SerializerMethodField()
    create_time = serializers.SerializerMethodField()
    unit_result = serializers.SerializerMethodField()
    skill_assessment_en = serializers.SerializerMethodField()
    skill_assessment_zh = serializers.SerializerMethodField()
    first_start_time = serializers.SerializerMethodField()
    last_start_time = serializers.SerializerMethodField()

    def get_skill_assessment_en(self, obj):
        skill_assessment_en = obj.skill_assessment_en
        if skill_assessment_en:
            return eval(skill_assessment_en)

    def get_skill_assessment_zh(self, obj):
        skill_assessment_zh = obj.skill_assessment_zh
        if skill_assessment_zh:
            return eval(skill_assessment_zh)

    def get_unit_result(self, obj):
        report_results = VirtualclassUnitReportAudit.objects.filter(unit_report_id=obj.id).all()
        result = []
        for report_result in report_results:
            user_info = UserInfo.objects.filter(id=report_result.audit_user_id).first()
            result.append({
                'report_result_id': report_result.id,
                'examine_time': utils.datetime_to_str(report_result.create_time),
                'examiner': user_info.realname if user_info else '',
                'remark': report_result.remark,
                'status': report_result.status
            })
        return result

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    def get_first_start_time(self, obj):
        if obj.first_start_time:
            return utils.datetime_to_str(obj.first_start_time)

    def get_last_start_time(self, obj):
        if obj.last_start_time:
            return utils.datetime_to_str(obj.last_start_time)

    def get_unit(self, obj):

        virtualclass = obj.virtual_class

        if virtualclass:

            return {
                'course_edition': virtualclass.lesson.course.course_edition.id,
                'course_level': virtualclass.lesson.course.course_level,
                'lesson_num': CourseLesson.objects.filter(unit_no=obj.unit_no, status=CourseLesson.ACTIVE).count(),
                'unit': obj.unit_no
            }

    class Meta:
        model = VirtualclassUnitReport
        fields = ('id', 'student_user', 'tutor_user', 'unit', 'submit_count', 'skill_assessment_en', 'skill_assessment_zh',
                  'classroom_performance_en', 'classroom_performance_zh', 'improvement_point_en',
                  'improvement_point_zh', 'learning_suggestion_en', 'learning_suggestion_zh', 'create_time',
                  'status', 'unit_result', 'first_start_time', 'last_start_time')


class FirstReportStudentSerializer(serializers.ModelSerializer):

    parent_user = ParentInfoSerializer()
    finish_course_sum = serializers.SerializerMethodField()  # 学生完课次数
    age = serializers.SerializerMethodField()  # 年龄

    def get_age(self, obj):
        if obj.birthday:
            return timezone.now().year - obj.birthday.year

    def get_finish_course_sum(self, obj):
        virtualclass_sum = VirtualclassInfo.objects.filter(virtual_class_member__student_user=obj, status=VirtualclassInfo.FINISH_NOMAL).count()
        if virtualclass_sum:
            return virtualclass_sum
        return 0

    class Meta:
        model = UserStudentInfo
        fields = ('id', 'real_name', 'parent_user', 'gender', 'age', 'finish_course_sum')


class FirstReportSerializer(serializers.ModelSerializer):

    unit = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()  # 上课时间
    tutor_user = TutorInfoSerializer()
    student_user = FirstReportStudentSerializer()
    examine_result = serializers.SerializerMethodField()  # 审核结果
    fine_result = serializers.SerializerMethodField()  # 罚金结果

    def get_fine_result(self, obj):
        report_fines = CourseReportFine.objects.filter(report_id=obj.id, type=CourseReportFine.FIRST_REPORT).all()
        result = []
        for report_fine in report_fines:
            user_infos = self.context.get('user_infos', {})
            user_info = user_infos.get(report_fine.user_id)
            result.append({
                'user': user_info.realname if user_info else '',
                'create_time': report_fine.create_time,
                'money': report_fine.money,
                'remark': report_fine.remark
            })
        return result

    def get_examine_result(self, obj):
        examine_result = VirtualclassFirstReportAudit.objects.filter(first_report_id=obj.id).first()
        if examine_result:
            user_infos = self.context.get('user_infos', {})
            user_info = user_infos.get(examine_result.audit_user_id)
            return {
                'examine_time': utils.datetime_to_str(examine_result.create_time),
                'examiner': user_info.realname if user_info else '',
            }

    def get_start_time(self, obj):
        if obj.start_time:
            return utils.datetime_to_str(obj.start_time)

    def get_unit(self, obj):
        try:
            virtualclass = obj.virtual_class
        except:
            virtualclass = None
        if virtualclass:
            return {
                'course_edition': virtualclass.lesson.course.course_edition_id,
                'course_level': virtualclass.lesson.course.course_level,
                'lesson_no': virtualclass.lesson_no
            }

    class Meta:
        model = VirtualclassFirstReport
        fields = ('id', 'start_time', 'tutor_user', 'student_user', 'unit', 'status',
                  'submit_count', 'examine_result', 'fine_result', 'create_time', 'read_status')


class FirstReportDetailSerializer(serializers.ModelSerializer):

    start_time = serializers.SerializerMethodField()  # 上课时间
    unit = serializers.SerializerMethodField()
    student_user = FirstReportStudentSerializer()
    tutor_user = TutorInfoSerializer()
    create_time = serializers.SerializerMethodField()  # 提交时间
    examine_result = serializers.SerializerMethodField()  # 审核结果

    def get_start_time(self, obj):
        if obj.start_time:
            return utils.datetime_to_str(obj.start_time)

    def get_create_time(self, obj):
        return utils.datetime_to_str(obj.create_time)

    def get_examine_result(self, obj):
        examine_results = VirtualclassFirstReportAudit.objects.filter(first_report_id=obj.id).all()
        result = []
        for examine_result in examine_results:
            user_info = UserInfo.objects.filter(id=examine_result.audit_user_id).first()
            result.append({
                'report_result_id': examine_result.id,
                'examine_time': utils.datetime_to_str(examine_result.create_time),
                'examiner': user_info.realname if user_info else '',
                'remark': examine_result.remark,
                'status': examine_result.status
            })
        return result

    def get_unit(self, obj):

        virtualclass = obj.virtual_class

        if virtualclass:

            return {
                'course_edition': virtualclass.lesson.course.course_edition.id,
                'course_level': virtualclass.lesson.course.course_level,
                'lesson_no': virtualclass.lesson_no
            }

    class Meta:
        model = VirtualclassFirstReport
        fields = ('id', 'start_time', 'student_user', 'tutor_user', 'unit', 'course_info_en', 'course_info_zh', 'core_knowledge_en',
                  'core_knowledge_zh', 'add_knowledge_en', 'add_knowledge_zh', 'classroom_feedback_en',
                  'classroom_feedback_zh', 'communication_suggestion_en', 'communication_suggestion_zh',
                  'suggest_course_info_en', 'suggest_course_info_zh', 'student_character_en', 'student_character_zh',
                  'student_background_en', 'student_background_zh', 'advisor_assistance_en', 'advisor_assistance_zh',
                  'create_time', 'status', 'examine_result', 'submit_count')
