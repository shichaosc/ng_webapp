from django import forms
from classroom.models import VirtualclassInfo, VirtualclassException
from student.models import UserStudentInfo


class VirtualclassExceptionForm(forms.ModelForm):

    class Meta:
        model = VirtualclassException
        fields = '__all__'

    def clean(self):
        virtual_class_id = self.cleaned_data.get('virtual_class_id')
        try:
            virtual_class_info = VirtualclassInfo.objects.get(id=virtual_class_id)
        except Exception as e:
            raise forms.ValidationError('{}-{}'.format('virtual_class_id不存在', e))


# class CourseAdviserForm(forms.ModelForm):
#
#     class Meta:
#         model = CourseAdviserStudent
#         fields = '__all__'
#
#     def clean(self):
#         student_id = self.cleaned_data.get('student_id')
#         try:
#             student = UserStudentInfo.objects.get(id=student_id)
#         except Exception as e:
#             raise forms.ValidationError('{}-{}'.format('student_id不存在', e))
#
#
# class LearnManagerForm(forms.ModelForm):
#
#     class Meta:
#         model = LearnManagerStudent
#         fields = '__all__'
#
#     def clean(self):
#         student_id = self.cleaned_data.get('student_id')
#         try:
#             student = UserStudentInfo.objects.get(id=student_id)
#         except Exception as e:
#             raise forms.ValidationError('{}-{}'.format('student_id不存在', e))
