from django import forms
from course.models import CourseInfo, CourseLesson, Courseware


class CoursewareForm(forms.Form):

    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super(CoursewareForm, self).__init__(*args, **kwargs)
        if course_id:
            self.fields['lesson'] = forms.ChoiceField(choices=[(o.id, o.lesson_name) for o in CourseLesson.objects.filter(course__id=course_id, status=CourseLesson.ACTIVE).order_by('lesson_no')])
        else:
            self.fields['lesson'] = forms.ChoiceField(choices=[(o.id, o.lesson_name) for o in CourseLesson.objects.filter(status=CourseLesson.ACTIVE).order_by('lesson_no')])

    lesson = forms.ChoiceField(choices=[(o.id, o.lesson_name) for o in CourseLesson.objects.filter(status=CourseLesson.ACTIVE).order_by('lesson_no')])
    # session = self.fields['session']

    cw_content = forms.FileField(label='file')
    # cw_type = forms.ChoiceField(label='type', choices=[('ppt', 'ppt'), ('pdf', 'pdf'), ('pptx', 'pptx')])


class HomeworkForm(forms.Form):

    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super(HomeworkForm, self).__init__(*args, **kwargs)
        if course_id:
            self.fields['session'] = forms.ChoiceField(choices=[(o.id, o.lesson_name) for o in CourseLesson.objects.filter(course__id=course_id, status=CourseLesson.ACTIVE).order_by('lesson_no')])
        else:
            self.fields['session'] = forms.ChoiceField(choices=[(o.id, o.lesson_name) for o in CourseLesson.objects.filter(status=CourseLesson.ACTIVE).order_by('lesson_no')])

    session = forms.ChoiceField(choices=[(o.id, o.lesson_name) for o in CourseLesson.objects.filter(status=CourseLesson.ACTIVE).order_by('lesson_no')])
    hw_content = forms.FileField(label='file', )


class TeachPlanForm(forms.Form):

    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super(TeachPlanForm, self).__init__(*args, **kwargs)
        # if course_id:
        #     self.fields['session'] = forms.ChoiceField(choices=[(o.id, o.session_name) for o in Session.objects.filter(course__id=course_id)])
        if course_id:
            self.fields['session'] = forms.ChoiceField(choices=[(o.id, o.lesson_name) for o in CourseLesson.objects.filter(course__id=course_id, status=CourseLesson.ACTIVE).order_by('lesson_no')])
        else:
            self.fields['session'] = forms.ChoiceField(choices=[(o.id, o.lesson_name) for o in CourseLesson.objects.filter(status=CourseLesson.ACTIVE).order_by('lesson_no')])

    session = forms.ChoiceField(choices=[(o.id, o.lesson_name) for o in CourseLesson.objects.all()])
    tp_content = forms.FileField(label='file', )
