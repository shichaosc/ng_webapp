from rest_framework import permissions


class AppointmentListPermission(permissions.BasePermission):

    message = '没有查看约课列表权限，请联系管理员'

    def has_permission(self, request, view):

        return True

        # permissions = request.session.get('permissions', [])
        # if 'appointment_list' in permissions:
        #     return True
        # return False
