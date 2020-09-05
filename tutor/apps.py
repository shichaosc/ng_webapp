from django.apps import AppConfig


class TutorInfoConfig(AppConfig):

    name = 'tutor'
    verbose_name = '老师个人信息'

    def ready(self):
        """
        在子类中重写此方法，以便在Django启动时运行代码。
        :return:
        """
        pass