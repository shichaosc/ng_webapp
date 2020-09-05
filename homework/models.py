from django.db import models
from course.models import CourseLesson


class HomeworkKnowledgePoint(models.Model):

    '''作业知识点考察内容表'''

    INVALID = 0
    VALID = 1

    STATUS_CHOICE = (
        (INVALID, 'Invalid'),
        (VALID, 'Valid')
    )

    label = models.CharField(max_length=31, help_text='考察内容')
    status = models.IntegerField(choices=STATUS_CHOICE, blank=True, null=True, help_text='状态，0：无效；1：有效')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'homework_knowledge_point'


class HomeworkOutlineInfo(models.Model):

    '''家庭作业大纲信息表'''

    NOT_FINISH = 0
    ACTIVE = 1
    ARCHIVED = 2
    DELETED = 3

    STATUS_CHOICE = (
        (NOT_FINISH, 'Not Finish'),
        (ACTIVE, 'Active'),
        (ARCHIVED, 'Archived')
    )

    lesson = models.ForeignKey(CourseLesson, on_delete=models.CASCADE, related_name='homework_outline')
    inspection_content = models.CharField(max_length=2047, help_text='考察内容')
    status = models.IntegerField(choices=STATUS_CHOICE, default=NOT_FINISH, blank=True, null=True, help_text='状态，0：草稿；1：有效；2：归档; 3:删除')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.lesson.lesson_no, self.get_status_display())

    class Meta:
        managed = False
        db_table = 'homework_outline_info'


class HomeworkOutlineGroup(models.Model):

    '''家庭作业大纲题目分组表'''

    MULTIPLE_CHOICE_QUESTION = 1
    FILL_IN_BLANK_QUESTION = 2
    CONNECTION_QUESTION = 3
    SORTING_QUESTION = 4
    READING_QUESTION = 5
    OTHER_QUESTION = 6

    TYPE_CHOICE = (
        (MULTIPLE_CHOICE_QUESTION, '选择题'),
        (FILL_IN_BLANK_QUESTION, '填空题'),
        (CONNECTION_QUESTION, '连线题'),
        (SORTING_QUESTION, '排序题'),
        (READING_QUESTION, '阅读题'),
        (OTHER_QUESTION, '其他')
    )

    lesson = models.ForeignKey(CourseLesson, on_delete=models.CASCADE, blank=True)
    outline = models.ForeignKey(HomeworkOutlineInfo, on_delete=models.CASCADE, blank=True, related_name='outline_group', help_text='家庭作业大纲标识')
    type = models.IntegerField(choices=TYPE_CHOICE, blank=True, help_text='题目类型，1：选择题；2：填空题；3：连线题；4：排序题；5：阅读题；6：其它')
    name = models.CharField(max_length=31, default='', blank=True)
    remark = models.CharField(max_length=127, default='', blank=True)
    quality = models.IntegerField(help_text='题目数量', blank=True)
    sort_no = models.IntegerField(help_text='大纲中分组排序编号', blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.lesson.lesson_no, self.name, self.get_type_display())

    class Meta:
        managed = False
        db_table = 'homework_outline_group'


class HomeworkQuestionInfo(models.Model):

    '''家庭作业题目信息表'''

    MULTIPLE_CHOICE_QUESTION = 1
    FILL_IN_BLANK_QUESTION = 2
    CONNECTION_QUESTION = 3
    SORTING_QUESTION = 4
    READING_QUESTION = 5
    OTHER_QUESTION = 6

    TYPE_CHOICE = (
        (MULTIPLE_CHOICE_QUESTION, 'Multiple Choice Question'),
        (FILL_IN_BLANK_QUESTION, 'fill in blank question'),
        (SORTING_QUESTION, 'Sorting Question'),
        (READING_QUESTION, 'Reading Question'),
        (OTHER_QUESTION, 'Other Question')
    )

    lesson = models.ForeignKey(CourseLesson, on_delete=models.CASCADE)
    outline = models.ForeignKey(HomeworkOutlineInfo, on_delete=models.CASCADE)
    outline_group = models.ForeignKey(HomeworkOutlineGroup, on_delete=models.CASCADE, related_name='homework_question')
    parent_question = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name='上级题目标识，仅仅阅读题下面的选择题和填空题才需要设置')
    type = models.IntegerField(choices=TYPE_CHOICE, help_text='题目类型，1：选择题；2：填空题；3：连线题；4：排序题；5：阅读题；6：其它')
    content = models.TextField(help_text='题目内容，JSON格式')
    knowledge_point_id = models.IntegerField(blank=True, null=True, help_text='题目考察的知识点标识')
    remark = models.CharField(max_length=127, blank=True, null=True, help_text='题目考察的知识点备注')
    remark_content = models.CharField(max_length=512, blank=True, null=True, help_text='题目考察的知识点备注内容')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.lesson.lesson_no, self.outline_group.name, self.get_type_display())

    class Meta:
        managed = False
        db_table = 'homework_question_info'
