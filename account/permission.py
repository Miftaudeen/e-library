from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import BasePermission

from account.models import User
from account.perms_constants import PERMS_CONSTANT_LIST, USER_PERMS_NAMES, MANAGER_NAME, ADMIN_NAME


def get_content_type():
    try:
        return ContentType.objects.get_for_model(User)
    except:
        return None


def get_all_permission_list():
    try:
        perms = Permission.objects.filter(content_type__app_label=User._meta.app_label,
                                          content_type__model=User._meta.model_name).exclude(
            codename__in=['add_user', 'delete_user', 'change_user', 'view_user']).order_by(
            'codename')
        return sorted(list(set([x.codename for x in perms])))
    except:
        return []


def get_user_permissions(user):
    try:
        perms = Permission.objects.filter(content_type__app_label=User._meta.app_label,
                                          content_type__model=User._meta.model_name, user=user).order_by('codename')
        return sorted(list(set([x.codename for x in perms])))
    except:
        return []


def get_all_permission_choices():
    try:
        perms = Permission.objects.filter(content_type__app_label=User._meta.app_label,
                                          content_type__model=User._meta.model_name).exclude(
            codename__in=['add_user', 'delete_user', 'change_user', 'view_user']).order_by('codename')
        return [(x.codename, str(x.codename).replace("_", " ").title()) for x in perms]
    except:
        return []


def get_user_permission_choices():
    try:
        perms = Permission.objects.filter(content_type__app_label=User._meta.app_label,
                                          content_type__model=User._meta.model_name, codename__in=USER_PERMS_NAMES).order_by('codename')
        return [(x.codename, str(x.codename).replace("_", " ").title()) for x in perms]
    except:
        return []


def create_default_permissions():
    ct = get_content_type()
    # print(ct)
    if not ct:
        return
    for perm in PERMS_CONSTANT_LIST:
        perm_dict = dict(perm)
        for key, val in perm_dict.items():
            try:
                Permission.objects.get(codename=key, content_type=ct)
            except:
                Permission.objects.create(codename=key, name=val, content_type=ct)


def delete_all_permission():
    perms = Permission.objects.filter(content_type__app_label=User._meta.app_label,
                                      content_type__model=User._meta.model_name)
    perms.delete()


def get_permission(codename):
    try:
        return Permission.objects.get(codename=codename)
    except:
        return None


def get_as_perm(constant):
    return "account.%s" % constant


def get_as_perms(constants):
    out = []
    if isinstance(constants, list):
        for i in constants:
            out.append(get_as_perm(i))
    else:
        out.append(get_as_perm(constants))
    return out


def get_or_create_permission(codename, name=None):
    ct = get_content_type()
    try:
        p = Permission.objects.get(codename=codename, content_type=ct)
    except:
        p = Permission.objects.create(codename=codename, name=name, content_type=ct)
    return p


def get_perm_info(perm):
    perm_dict = dict(perm)
    for key, val in perm_dict.items():
        return key, val


class ManagerPermission(BasePermission):

    def has_permission(self, request, view):
        user_perms = get_user_permissions(request.user)
        if MANAGER_NAME in user_perms or request.user.is_staff:
            return True
        return False


class AdminPermission(BasePermission):

    def has_permission(self, request, view):
        user_perms = get_user_permissions(request.user)
        if ADMIN_NAME in user_perms or request.user.is_staff:
            return True
        return False
