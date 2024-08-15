# from django.http import HttpResponseForbidden
# from django.utils.deprecation import MiddlewareMixin
# from django.urls import resolve
# from .models import Vendor
#
#
# class RolePermissionMiddleware(MiddlewareMixin):
#     def process_view(self, request, view_func, view_args, view_kwargs):
#         if not request.user.is_authenticated:
#             return HttpResponseForbidden("شما باید وارد بشید")
#
#         if not isinstance(request.user, Vendor):
#             return HttpResponseForbidden("کاربر نامعتبر")
#
#         view_name = resolve(request.path_info).url_name
#
#         role_based_views = {
#             'owner': ['edit_profile', 'profile'],
#             'manager': ['edit_profile', 'profile'],
#             'operator': ['edit_profile', 'profile'],
#         }
#
#         if request.user.is_owner:
#             return None
#
#         if request.user.is_manager:
#             if view_name in role_based_views['owner']:
#                 return HttpResponseForbidden("شما دسترسی ندارید به این صفحه")
#             return None
#
#         if request.user.is_operator:
#             if view_name in role_based_views['owner'] or view_name in role_based_views['manager']:
#                 return HttpResponseForbidden("شما دسترسی ندارید به این صفحه")
#             return None
#
#         return None
