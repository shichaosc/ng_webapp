from django.conf.urls import url, include

from django.views.generic import TemplateView, RedirectView

from man import views as man_view
from course import views as course_view
from classroom import views as classroom_view
from tutor import views as tutor_view
from activity import views as activity_view
from scheduler import views as scheduler_view

# urls for management panel
urlpatterns = [
    url(r'^$', man_view.man_home, name='man_home'),

    url(r'^course/preview/', course_view.preview, name='course_preview'),
    url(r'^course/upload/', course_view.upload, name='course_upload'),
    url(r'^course/questionnaire/', course_view.questionnaire, name='questionnaire'),
    url(r'^examassement/preview/', course_view.assessment_preview, name='assessment_preview'),
    url(r'^examassement/list/', course_view.examassement_list, name='examassement_list'),
    url(r'^course/homework/', course_view.homework, name='homework'),
    url(r'^course/homeworkupload/', course_view.homeworkupload, name='homeworkupload'),
    url(r'^course/teachplan/', course_view.teachplan, name='teachplan'),
    url(r'^course/teachplanupload/', course_view.teachplanupload, name='teachplanupload'),
    url(r'^tutor/list_all/', tutor_view.list_all_tutors, name='all_tutor_list'),
    url(r'^virtualclass/list/', classroom_view.list_class, name='vc_list'),
    # 教室转换
    url(r'^virtualclass/convert_list/', classroom_view.convert_list, name='Convert_list'),
    # 教师管理
    url(r'^tutor/management/', tutor_view.management, name='tutor_management'),

    url(r'^course/get_courses_by_programme/$', course_view.get_courses_by_programme, name='get_courses_by_programme'),
    url(r'^course/get_tutor_courses/$', course_view.get_tutor_courses, name='get_tutor_courses'),

    url(r'^tutor/tutor_grade_add/$', tutor_view.tutor_grade_add, name='tutor_grade_add'),

    url(r'^activity/rechargerecordsquery/', activity_view.rechargerecordsquery, name='rechargerecordsquery'),

    url(r'^activity/setfreedelivery/', activity_view.setfreedelivery, name='setfreedelivery'),

    # url(r'^course/preview/', man_view.preview, name='course_preview'),
    url(r'^questionnaire_upload/', course_view.questionnaire_upload, name='questionnaire_upload'),
    url(r'^questionnaire_delete/', course_view.questionnaire_delete, name='questionnaire_delete'),

    url(r'^exambank/preview/', course_view.exambank_preview, name='exambank_preview'),

    url(r'^tutor/tutor_salary/', tutor_view.tutor_salary, name='tutor_salary'),
    url(r'^tutor/tutor_salary_detail/', tutor_view.tutor_salary_detail, name='tutor_salary_detail'),
    url(r'^tutor/update_pay_status/', tutor_view.update_pay_status, name='update_pay_status'),

    url(r'^exambank/list/', course_view.exambank_list, name='exambank_list'),

    url(r'^exambank/edit/(?P<id>[0-9]+)/$', course_view.exambank_edit, name='exambank_edit'),
    url(r'^exambank/upload/(?P<id>[0-9]+)/$', course_view.exambank_upload, name='exambank_upload'),

    url(r'^examaassessment/upload/', course_view.assessment_upload, name='assessment_upload'),

    # 拓课转声网教室
    url(r'^virtualclass/revert/', classroom_view.revert, name='vc_revert'),
    # 拓课巡课
    url(r'^virtualclass/monitor_tk/', classroom_view.monitor_tk, name='vc_monitor_tk'),

    # url(r'^questionnaire_delete/' , man_view.questionnaire_delete , name = 'questionnaire_delete' ),
    # url(r'^exambank/preview/', man_view.exambank_preview, name='exambank_preview'),
    #
    url(r'^virtualclass/monitor/', classroom_view.monitor, name='vc_monitor'),
    # url(r'^virtualclass/list/', man_view.list_class, name='vc_list'),
    #
    # url(r'^accounts/withdraw_review/', man_view.withdrawal_review, name='withdrawal_review'),
    #
    # url(r'^explorer/', include('explorer.urls')),
    #
    # url(r'^tutor/', include('tutor.urls')),
    # # simon

    # # 拓课转声网教室
    # url(r'^virtualclass/revert/', man_view.revert, name='vc_revert'),
    # url(r'^course/bunch_upload/', man_view.bunch_upload, name='bunch_upload'),
    # url(r'^campaign/list/', man_view.april_refer_list, name='april_refer_list'),
    # url(r'^campaign/detail/', man_view.april_refer_detail, name='april_refer_detail'),
    # url(r'^campaign/mobile/', man_view.april_refer_mobile, name='april_refer_mobile'),
    url(r'^man_event/', scheduler_view.man_event, name='man_event'),
    url(r'^get_tutor_status/', tutor_view.get_tutor_status, name='get_tutor_status'),
    url(r'^set_tutor_status/', tutor_view.set_tutor_status, name='set_tutor_status'),
    url(r'^set_tutor_area/', tutor_view.set_tutor_area, name='set_tutor_area'),
    url(r'^questions/', course_view.questions, name='questions'),

]
