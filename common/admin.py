from django.contrib import admin
from common.models import *
from tutor.models import TutorInfo
from student.models import UserStudentInfo, UserParentInfo

# Register your models here.


@admin.register(CommonAmbassadorCode)
class CommonAmbassadorCodeAdmin(admin.ModelAdmin):

    list_filter = ('is_used', )
    raw_id_fields = ('ambassador_user', )
    search_fields = ('ambassador_user__username', 'ambassador_user__email', 'ambassador_user__phone')
    list_display = ('id', 'ambassador_user', 'code', 'is_used')


@admin.register(CommonAppversion)
class CommonAppversionAdmin(admin.ModelAdmin):

    list_filter = ('role', )
    list_display = ('id', 'role', 'user', 'appname', 'deviceid', 'devicename', 'versionnum')

    def user(self, common_appversion):

        role = common_appversion.role
        user = None
        if role == CommonAppversion.PARENT:
            user = UserParentInfo.objects.filter(id=common_appversion.user_id).first()
        elif role == CommonAppversion.CHILDREN:
            user = UserStudentInfo.objects.filter(id=common_appversion.user_id).first()
        elif role == CommonAppversion.TEACHER:
            user = TutorInfo.objects.filter(id=common_appversion.user_id).first()
        elif role == CommonAppversion.AMBASSADOR:
            user = UserAmbassadorInfo.objects.filter(id=common_appversion.user_id).first()
        return user


@admin.register(CommonBussinessRule)
class CommonBussinessRuleAdmin(admin.ModelAdmin):

    list_filter = ('rule_type', 'local_area')
    list_display = ('id', 'course_edition', 'class_type', 'rule_type', 'user_level', 'local_area', 'valid_start', 'valid_end', 'remark')


@admin.register(CommonRuleFormula)
class CommonRuleFormulaAdmin(admin.ModelAdmin):

    list_filter = ('rule_id', )
    raw_id_fields = ('rule', )
    list_display = ('id', 'rule_id', 'valid_start', 'valid_end', 'min_amount', 'max_amount', 'amount')

    def valid_start(self, rule_formula):
        if rule_formula.rule:
            return rule_formula.rule.valid_start

    def valid_end(self, rule_formula):
        if rule_formula.rule:
            return rule_formula.rule.valid_end


@admin.register(CommonCoupon)
class CommonCouponAdmin(admin.ModelAdmin):

    list_filter = ('status', )
    search_fields = ('code', )
    list_display = ('code', 'valid_start_time', 'valid_end_time', 'amount', 'discount', 'status')


@admin.register(CommonStudentCoupon)
class CommonStudentCouponAdmin(admin.ModelAdmin):

    list_filter = ('status', )
    search_fields = ('code', )


@admin.register(UserConfig)
class UserConfigAdmin(admin.ModelAdmin):

    list_filter = ('role', )


admin.site.register(ExchangeRate)
