from django.db.utils import IntegrityError
from rest_framework import viewsets, exceptions
# from users.serializer import MenuSerializer, RoleSerializer, CmsUserRoleSerializer, \
#     RoleListSerializer, CmsUserSerializer, MenuListSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from queue import Queue
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import logging
from manage.models import UserInfo
from manage.serializer import UserInfoSerializer

logger = logging.getLogger(__name__)


# class LoginView(APIView):
#
#     def post(self, request):
#         user_name = request.data.get('username')
#         password = request.data.get('password')
#         if not user_name or not password:
#             return Response({'message': '参数缺失', 'code': 1}, status=status.HTTP_200_OK)
#         user = CmsUser.objects.filter(username=user_name, is_active=CmsUser.ACTIVE).first()
#         if not user:
#             return Response({'message': '用户名不存在', 'code': 1}, status=status.HTTP_200_OK)
#         encry_password = encrypt_passwd(password, user.salt)
#         if user.password != encry_password:
#             return Response({'message': '密码错误', 'code': 1}, status=status.HTTP_200_OK)
#         if user.is_active == 2:
#             return Response({'message': '账号被禁止', 'code': 1}, status=status.HTTP_200_OK)
#         serializer = CmsUserSerializer(user)
#
#         request.session['user'] = serializer.data
#         # 添加日志
#         try:
#             params = dict(user_id=user.id, operation='登陆', operate_type='用户', operate_name=user.username, type=1)
#             login_signal.send(sender=self.request, params=params)
#         except Exception as e:
#             logger.error('insert user operation fail, error={}'.format(e))
#
#         return Response(
#             {
#                 'message': 'success',
#                 'code': 0,
#                 'user': {
#                     'realname': user.realname,
#                     'username': user.username
#                 }
#             },
#             status=status.HTTP_200_OK)


class LoginView(APIView):

    def post(self, request):
        user_name = request.data.get('username')
        if not user_name:
            return Response({'message': '参数缺失', 'code': 1}, status=status.HTTP_200_OK)

        user = UserInfo.objects.filter(username=user_name, status=UserInfo.ENABLE).first()
        if not user:
            return Response({'message': '用户名不存在', 'code': 1}, status=status.HTTP_200_OK)

        serializer = UserInfoSerializer(user)

        request.session['user'] = serializer.data
        return Response(
            {
                'message': 'success',
                'code': 0,
                'user': {
                    'realname': user.realname,
                    'username': user.username
                }
            },
            status=status.HTTP_200_OK)




class LogOutView(APIView):

    def post(self, request):
        request.session.flush()
        return Response({'message': 'success', 'code': 0}, status=status.HTTP_200_OK)


# class MenuViewSet(viewsets.ModelViewSet):
#
#     permission_classes = (IsAuthenticated,)
#
#     queryset = Menu.objects.all().order_by('sort')
#     filter_backends = (DjangoFilterBackend, filters.SearchFilter)
#     filter_fields = ('type', )
#     search_fields = ('name', )
#
#     def permission_denied(self, request, message=None):
#         '''
#         没有权限时的返回值
#         :param request:
#         :param message:
#         :return:
#         '''
#         if not message:
#             raise exceptions.NotAuthenticated()
#         raise exceptions.PermissionDenied(detail=message)
#
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
#
#     def get_serializer_class(self):
#         if self.action == 'list':
#             return MenuListSerializer
#         return MenuSerializer
#
#     def get_queryset(self):
#         all = self.request.query_params.get('all')
#         if all:
#             menus = Menu.objects.all().order_by('type').order_by('sort')
#             return menus
#         user = self.request.session.get('user')
#         roles = Role.objects.filter(cmsuser__id=user.get('id')).all()
#         menus = Menu.objects.filter(role__in=roles).order_by('sort')
#
#         return menus
#
#     @action(methods=['get'], detail=False)
#     def menu_list(self, request):
#         queue = Queue()
#         menus = self.get_queryset()
#         menu_list = []
#         permissions = []
#         for menu in menus:
#             permissions.append(menu.url_name)
#             if menu.aParent is None:
#                 menu_dict = {
#                     'id': menu.id,
#                     'name': menu.name,
#                     'type': menu.type,
#                     'sort': menu.sort,
#                     'icon': menu.icon,
#                     'children': []
#                 }
#                 menu_list.append(menu_dict)
#                 continue
#             obj = self.add_child(menu_list, menu)
#             if obj:
#                 queue.put(obj)
#         queue_length = queue.qsize()
#         while not queue.empty():
#             loop = queue_length - 1
#             menu = queue.get()
#             obj = self.add_child(menu_list, menu)
#             if obj:
#                 queue.put(obj)
#             if loop == 0:
#                 if queue_length == queue.qsize():
#                     break
#                 queue_length = queue.qsize()
#         request.session['permissions'] = permissions  # 权限添加到session
#
#         return Response(menu_list, status=status.HTTP_200_OK)
#
#     def add_child(self, menu_list, obj=None):
#         if obj is None:
#             return
#         for menu in menu_list:
#
#             if menu['id'] == obj.aParent.id:
#                 menu_dict = {
#                     'id': obj.id,
#                     'type': obj.type,
#                     'name': obj.name,
#                     'url': obj.url,
#                     'icon': obj.icon,
#                     'sort': obj.sort,
#                     'children': []
#                 }
#                 menu['children'].append(menu_dict)
#                 return
#             else:
#                 obj = self.add_child(menu['children'], obj)
#                 if obj is None:
#                     return
#         return obj


# class RoleViewSet(viewsets.ModelViewSet):
#
#     queryset = Role.objects.all()
#     filter_backends = (DjangoFilterBackend, filters.SearchFilter)
#     search_fields = ('name',)
#     permission_classes = (IsAuthenticated,)
#
#     def permission_denied(self, request, message=None):
#         '''
#         没有权限时的返回值
#         :param request:
#         :param message:
#         :return:
#         '''
#         if not message:
#             raise exceptions.NotAuthenticated()
#         raise exceptions.PermissionDenied(detail=message)
#
#     def get_permissions(self):
#         if self.action == 'retrieve':  # 这里的 action 只有使用了 viewset才有
#             return [IsAuthenticated(), RoleListPermission()]
#         # elif self.action == 'create':
#         #     return (IsAuthenticated, AddRolePermission)
#         elif self.action == 'destroy':
#             return [IsAuthenticated(), DeleteRolePermission()]
#         elif self.action == 'edit':
#             return [IsAuthenticated(), EditRolePermission()]
#         elif self.action == 'update':
#             return [IsAuthenticated(), ChangeRoleStatusPermission()]
#         elif self.action == 'add':
#             return [IsAuthenticated(), AddRolePermission()]
#         return [IsAuthenticated(), ]
#
#     def get_serializer_class(self):
#         if self.action == 'list':
#             return RoleListSerializer
#         return RoleSerializer
#
#     def get_queryset(self):
#         roles = Role.objects.all()
#         return roles
#
#     @action(methods=['post'], detail=False)
#     def add(self, request):
#         role_name = request.data.get('name')
#         # menu_ids = request.data.get('menu_ids', [])
#         role_status = request.data.get('status', 1)
#         role_description = request.data.get('description', '')
#         # menus = Menu.objects.filter(id__in=menu_ids).all()
#         role = Role.objects.create(name=role_name, status=role_status, description=role_description)
#         # role.menu = menus
#         role.save()
#         # 添加日志
#         try:
#             params = dict(operation='添加角色', operate_type='角色', operate_name=role.name)
#             log_signal.send(sender=request, params=params)
#         except Exception as e:
#             logger.error('insert user operation fail, error={}'.format(e))
#
#         return Response(status=status.HTTP_200_OK)
#
#     @action(methods=['put'], detail=True)
#     def edit(self, request, pk):
#
#         menu_ids = request.data.get('menu_ids')
#         role = self.get_object()
#         menus = Menu.objects.filter(id__in=menu_ids).all()
#         role.menu = menus
#         role.save()
#         # 添加日志
#         try:
#             params = dict(operation='编辑角色权限', operate_type='角色', operate_name=role.name)
#             log_signal.send(sender=request, params=params)
#         except Exception as e:
#             logger.error('insert user operation fail, error={}'.format(e))
#
#         return Response(status=status.HTTP_200_OK)
#
#     @action(methods=['get'], detail=True, permission_classes=[IsAuthenticated,])
#     def menu(self, request, pk):
#         role = self.get_object()
#         role_menu = Menu.objects.filter(role=role).values('id')
#         menus = Menu.objects.all()
#         queue = Queue()
#         menu_list = []
#         permissions = []
#         for menu in menus:
#             #permissions.append(menu.url_name)
#             if menu.aParent is None:
#                 menu_dict = {
#                     'id': menu.id,
#                     'name': menu.name,
#                     'type': menu.type,
#                     'sort': menu.sort,
#                     'children': []
#                 }
#                 if menu.id in role_menu:
#                     menu_dict['role'] = 1
#                 menu_list.append(menu_dict)
#                 continue
#             obj = self.add_child(menu_list, role_menu, menu)
#             if obj:
#                 queue.put(obj)
#         queue_length = queue.qsize()
#         while not queue.empty():
#             loop = queue_length - 1
#             menu = queue.get()
#             # permissions.append(menu.url_name)
#             obj = self.add_child(menu_list, menu)
#             if obj:
#                 queue.put(obj)
#             if loop == 0:
#                 if queue_length == queue.qsize():
#                     break
#                 queue_length = queue.qsize()
#         return Response(menu_list, status=status.HTTP_200_OK)
#
#     def add_child(self, menu_list, role_menu, obj=None):
#         if obj is None:
#             return
#         for menu in menu_list:
#
#             if menu['id'] == obj.aParent.id:
#                 menu_dict = {
#                     'id': obj.id,
#                     'type': obj.type,
#                     'name': obj.name,
#                     'url': obj.url,
#                     'children': []
#                 }
#                 if obj in role_menu:
#                     menu_dict['role'] = 1
#                 menu['children'].append(menu_dict)
#                 return
#             else:
#                 obj = self.add_child(menu['children'], obj)
#                 if obj is None:
#                     return
#         return obj
#
#     def destroy(self, request, *args, **kwargs):
#
#         response = super().destroy(request, *args, **kwargs)
#         # 添加日志
#         try:
#             role = self.get_object()
#             params = dict(operation='删除角色', operate_type='角色', operate_name=role.name)
#             log_signal.send(sender=self.request, params=params)
#         except Exception as e:
#             logger.error('insert user operation log fail, error={}'.format(e))
#         return response
#
#     def update(self, request, *args, **kwargs):
#
#         response = super().update(request, *args, **kwargs)
#         # 添加日志
#         try:
#             role = self.get_object()
#             params = dict(operation='修改角色状态', operate_type='角色', operate_name=role.name)
#             log_signal.send(sender=self.request, params=params)
#         except Exception as e:
#             logger.error('insert user operation log fail, error={}'.format(e))
#         return response


# class UserViewSet(viewsets.ModelViewSet):
#
#     permission_classes = (IsAuthenticated,)
#     filter_backends = (DjangoFilterBackend, filters.SearchFilter)
#     filter_class = CmsUserFilter
#     # serializer_class = CmsUserRoleSerializer
#     queryset = CmsUser.objects.all()
#
#     def permission_denied(self, request, message=None):
#         '''
#         没有权限时的返回值
#         :param request:
#         :param message:
#         :return:
#         '''
#         if not message:
#             raise exceptions.NotAuthenticated()
#         raise exceptions.PermissionDenied(detail=message)
#
#     def get_serializer_class(self):
#
#         if self.action == 'update':
#             return CmsUserSerializer
#         return CmsUserRoleSerializer
#
#     def get_permissions(self):
#         # if self.action == 'retrieve':  # 这里的 action 只有使用了 viewset才有
#         #     return [IsAuthenticated(), UserListPermission()]
#         # # elif self.action == 'create':
#         # #     return (IsAuthenticated, AddRolePermission)
#         # elif self.action == 'destroy':
#         #     return [IsAuthenticated(), DeleteUserPermission()]
#         # elif self.action == 'edit':
#         #     return [IsAuthenticated(), EditUserPermission()]
#         # elif self.action == 'update':
#         #     return [IsAuthenticated(), UserStatusChangePermission()]
#         # elif self.action == 'add':
#         #     return [IsAuthenticated(), AddManagerUserPermission()]
#         return [IsAuthenticated(), ]
#
#     @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated,])
#     def add(self, request):
#         username = request.data.get('username')
#         work_address = request.data.get('work_address')
#         realname = request.data.get('realname')
#         role_id = request.data.get('role_id', [])
#         # dept_id = request.data.get('dept_id')
#         phone = request.data.get('phone')
#         password = request.data.get('password', '123456')
#         salt = utils.random_str(6)
#         password = utils.encrypt_passwd(password, salt)
#         role = Role.objects.filter(id__in=role_id).all()
#         try:
#             user = CmsUser.objects.create(username=username, work_address=work_address, realname=realname,
#                            phone=phone, salt=salt, password=password, is_active=1)
#         except IntegrityError as e:
#             return JsonResponse(code=1, msg='用户名已存在', status=status.HTTP_200_OK)
#         if role:
#             user.role = role
#         user.save()
#         # 添加日志
#         try:
#             params = dict(operation='添加用户', operate_type='用户', operate_name=user.username)
#             log_signal.send(sender=request, params=params)
#         except Exception as e:
#             logger.error('insert user operation fail, error={}'.format(e))
#
#         return Response(status=status.HTTP_200_OK)
#
#     @action(methods=['put'], detail=True, permission_classes=[IsAuthenticated, ])
#     def edit(self, request, pk):
#         username = request.data.get('username')
#         work_address = request.data.get('work_address')
#         realname = request.data.get('realname')
#         role_id = request.data.get('role_id', [])
#         # dept_id = request.data.get('dept_id')
#         phone = request.data.get('phone')
#         # dept = Department.objects.filter(id=dept_id).first()
#         # if dept:
#         #     role = Role.objects.filter(id__in=role_id, department=dept).all()
#         # else:
#         role = Role.objects.filter(id__in=role_id).all()
#         user = CmsUser.objects.get(id=pk)
#         user.username = username
#         user.work_address = work_address
#         user.realname = realname
#         user.phone = phone
#         if role:
#             user.role = role
#         user.save()
#         # 添加日志
#         try:
#             params = dict(operation='编辑用户信息', operate_type='用户', operate_name=user.username)
#             log_signal.send(sender=request, params=params)
#         except Exception as e:
#             logger.error('insert user operation fail, error={}'.format(e))
#
#         return Response(status=status.HTTP_200_OK)
#
#     @action(methods=['put'], detail=True, permission_classes=[IsAuthenticated, ])
#     def edit_status(self, request, pk):
#         is_active = request.data.get('is_active')
#         user = self.get_object()
#         user.is_active = is_active
#         user.save()
#         # 添加日志
#         if int(is_active) == 1:
#             operation = '启用用户'
#         else:
#             operation = '禁用用户'
#         # 添加日志
#         try:
#             params = dict(operation=operation, operate_type='用户', operate_name=user.username)
#             log_signal.send(sender=request, params=params)
#         except Exception as e:
#             logger.error('insert user operation fail, error={}'.format(e))
#
#         return Response(status=status.HTTP_200_OK)
#
#     @action(methods=['put'], detail=True, permission_classes=[IsAuthenticated, ])
#     def resetpwd(self, request, pk):
#         password = '123456'
#         salt = utils.random_str(6)
#         # password = utils.encrypt_passwd(password, salt)
#         user = self.get_object()
#         user.salt = salt
#         user.password = password
#         user.save()
#         # 添加日志
#         try:
#             params = dict(operation='重置密码', operate_type='用户', operate_name=user.username)
#             log_signal.send(sender=request, params=params)
#         except Exception as e:
#             logger.error('insert user operation fail, error={}'.format(e))
#
#         return Response(status=status.HTTP_200_OK)
#
#     def destroy(self, request, *args, **kwargs):
#         response = super().destroy(request, *args, **kwargs)
#         cms_user = self.get_object()
#         # 添加日志
#         try:
#             params = dict(operation='删除用户', operate_type='用户', operate_name=cms_user.username)
#             log_signal.send(sender=self.request, params=params)
#         except Exception as e:
#             logger.error('insert user operation fail, error={}'.format(e))
#         return response
#
#     @action(methods=['get'], detail=False)
#     def userlist(self, request):
#         role = request.query_params.get('role')
#
#         if role and role not in ('learn_manager', 'course_adviser'):
#             return JsonResponse(code=1, msg='参数错误', status=status.HTTP_200_OK)
#         if role:
#             if role == 'learn_manager':
#                 users = UserInfo.objects.filter(role__id=RoleInfo.XG_USER_ID, status=UserInfo.ENABLE).all()
#             else:
#                 users = UserInfo.objects.filter(role__id=RoleInfo.ADVISER_USER_ID, status=UserInfo.ENABLE).all()
#         else:
#             users = UserInfo.objects.filter(role__id__in=(RoleInfo.ADVISER_USER_ID, RoleInfo.XG_USER_ID), status=UserInfo.ENABLE).all().distinct()
#
#         serializer = UserInfoSerializer(users, many=True)
#         return JsonResponse(code=0, msg='success', data=serializer.data, status=status.HTTP_200_OK)
