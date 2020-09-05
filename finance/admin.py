from django.contrib import admin
from finance.models import BalanceChange, BuyPackage, CoursePackage, ClasstypePrice, \
    RechargeOrder, Transfer, UserCoupon, StripePayMethodInfo, TutorSalary, AccountBalance, \
    Payment, OrderReceipt
from tutor.models import TutorInfo
from student.models import UserStudentInfo, UserParentInfo
from ambassador.models import UserAmbassadorInfo
from django.db.models import Q


@admin.register(AccountBalance)
class AccountBalanceAdmin(admin.ModelAdmin):

    list_filter = ('type', 'account_class')
    list_display = ('id', 'balance', 'type', 'account_class', 'rate', 'state')
    search_fields = ('parent_user__username', 'parent_user__email', 'parent_user__phone')
    raw_id_fields = ('parent_user',)
    list_per_page = 50


@admin.register(BalanceChange)
class BalanceChangeAdmin(admin.ModelAdmin):

    list_filter = ('reason', )
    list_display = ('id', 'reference', 'reason', 'user', 'role', 'amount')
    search_fields = ('reference', )
    raw_id_fields = ('balance', )
    list_per_page = 50

    def get_search_results(self, request, queryset, search_term):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        use_distinct = False
        if search_term:
            queryset = queryset.filter(reference=search_term)

        return queryset, use_distinct

    def user(self, obj):
        user = None
        if obj.role == BalanceChange.PARENT:
            user = UserParentInfo.objects.filter(id=obj.user_id).first()
        elif obj.role == BalanceChange.CHILDREN:
            user = UserStudentInfo.objects.filter(id=obj.user_id).first()
        elif obj.role == BalanceChange.TEACHER:
            user = TutorInfo.objects.filter(id=obj.user_id).first()
        elif obj.role == BalanceChange.AMBASSADOR:
            user = UserAmbassadorInfo.objects.filter(id=obj.user_id).first()
        return user


@admin.register(RechargeOrder)
class RechargeOrderAdmin(admin.ModelAdmin):

    search_fields = ('parent_name', )
    raw_id_fields = ('parent_user', 'sg_class', 'referrer_user')
    list_filter = ('recharge_type', 'status')
    list_display = ('parent_user_name', 'order_no', 'status')
    ordering = ('-id', )
    list_per_page = 50

    def get_search_results(self, request, queryset, search_term):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        use_distinct = False
        if search_term:
            queryset = queryset.filter(Q(parent_user__username=search_term)|Q(parent_user__email=search_term)|Q(parent_user__phone=search_term))

        return queryset, use_distinct

    def parent_user_name(self, obj):
        user_parent_info = UserParentInfo.objects.filter(id=obj.parent_user_id).only('username').first()
        return user_parent_info.username


@admin.register(BuyPackage)
class BuyPackageAdmin(admin.ModelAdmin):

    list_display = ('id', 'class_type', 'parent_user', 'course_edition', 'valid_start_time', 'valid_end_time')
    search_fields = ('parent_user__username', 'parent_user__email', 'parent_user__phone')


class CoursePackageAdmin(admin.ModelAdmin):

    # list_display = ('id', 'class_type', 'course_edition', 'prices', 'cash_price', 'duration', 'duration_type')
    search_fields = ('id', )
    # list_filter = ('duration_type', )


class ClasstypePriceAdmin(admin.ModelAdmin):

    list_display = ('id', 'class_type', 'course_edition', 'prices')
    search_fields = ('id',)


class TransferAdmin(admin.ModelAdmin):

    list_display = ('id', 'amount', 'recipient_user', 'transfer_user')


class UserCouponAdmin(admin.ModelAdmin):

    list_display = ('id', 'parent_user', 'code', 'valid_start_time', 'valid_end_time', 'used')
    list_filter = ('used', )
    search_fields = ('parent_user__username', 'parent_user__email', 'parent_user__phone')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_filter = ('type', 'status', 'channel')
    search_fields = ('order__id', )
    raw_id_fields = ('order', )
    list_per_page = 50


@admin.register(OrderReceipt)
class OrderReceiptAdmin(admin.ModelAdmin):

    search_fields = ('order__id', )
    raw_id_fields = ('order', )
    list_per_page = 50


admin.site.register(CoursePackage, CoursePackageAdmin)
admin.site.register(ClasstypePrice, ClasstypePriceAdmin)
admin.site.register(Transfer, TransferAdmin)
admin.site.register(UserCoupon, UserCouponAdmin)
admin.site.register(StripePayMethodInfo)
admin.site.register(TutorSalary)

