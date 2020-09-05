from rest_framework import permissions


class StudentListPermission(permissions.BasePermission):

    message = '没有查看学生列表权限，请联系管理员'

    def has_permission(self, request, view):

        return True

        # permissions = request.session.get('permissions', [])
        # if 'student_list' in permissions:
        #     return True
        # return False


class OldStudentListPermission(permissions.BasePermission):

    message = '没有查看学生列表权限，请联系管理员'

    def has_permission(self, request, view):

        return True

        # permissions = request.session.get('permissions', [])
        # if 'oldstudent_list' in permissions:
        #     return True
        # return False


class StudentDetailPermission(permissions.BasePermission):

    message = '没有查看学生详情权限，请联系管理员'

    def has_permission(self, request, view):

        return True

        # permissions = request.session.get('permissions', [])
        # if 'student_detail' in permissions:
        #     return True
        # return False


class AddRemarkPermission(permissions.BasePermission):

    message = '没有添加备注权限，请联系管理员'

    def has_permission(self, request, view):

        return True

        # permissions = request.session.get('permissions', [])
        # if 'role_edit' in permissions:
        #     return True
        # return False


# class ChangeRoleStatusPermission(permissions.BasePermission):
#
#     message = '没有修改角色状态权限，请联系管理员'
#
#     def has_permission(self, request, view):
#
#         permissions = request.session.get('permissions', [])
#
#         if 'role_status_change' in permissions:
#             return True
#         return False
#
#
# class DeleteRolePermission(permissions.BasePermission):
#
#     message = '没有删除角色权限， 请联系管理员'
#
#     def has_permission(self, request, view):
#
#         permissions = request.session.get('permissions', [])
#
#         if 'role_delete' in permissions:
#             return True
#         return False
#
#
# class AddRolePermission(permissions.BasePermission):
#
#     message = '没有添加角色权限，请联系管理员'
#
#     def has_permission(self, request, view):
#
#         permissions = request.session.get('permissions', [])
#         if 'role_add' in permissions:
#             return True
#         return False
#
#
# class UserListPermission(permissions.BasePermission):
#
#     message = '没有查看用户列表权限，请联系管理员'
#
#     def has_permission(self, request, view):
#         permissions = request.session.get('permissions', [])
#         if 'user_list' in permissions:
#             return True
#         return False
#
#
# class AddManagerUserPermission(permissions.BasePermission):
#
#     message = '没有添加后台用户权限，请联系管理员'
#
#     def has_permission(self, request, view):
#
#         permissions = request.session.get('permissions', [])
#
#         if 'user_add' in permissions:
#             return True
#         return False
#
#
# class DeleteUserPermission(permissions.BasePermission):
#
#     message = '没有删除用户权限，请联系管理员'
#
#     def has_permission(self, request, view):
#
#         permissions = request.session.get('permissions', [])
#         if 'user_delete' in permissions:
#             return True
#         return False
#
#
# class UserStatusChangePermission(permissions.BasePermission):
#
#     message = '没有切换工作人员状态权限，请联系管理员'
#
#     def has_permission(self, request, view):
#
#         permissions = request.session.get('permissions', [])
#
#         if 'user_status_change' in permissions:
#             return True
#         return False
#
#
# class EditUserPermission(permissions.BasePermission):
#
#     message = '没有修改工作人员信息权限，请联系管理员'
#
#     def has_permission(self, request, view):
#
#         permissions = request.session.get('permissions', [])
#
#         if 'user_edit' in permissions:
#             return True
#         return False
#
