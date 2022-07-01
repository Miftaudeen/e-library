
MANAGER_NAME = 'Manager'
ADMIN_NAME = 'Admin'
STUDENT_NAME = 'Student'

MANAGER = ((MANAGER_NAME, 'Manages the Library'),)
ADMIN = ((ADMIN_NAME, 'Administers the Library and the manager'),)
STUDENT = ((ADMIN_NAME, 'Requests books from the library'),)

PERM_CHOICES = (
    (MANAGER_NAME, MANAGER_NAME),
    (ADMIN_NAME, ADMIN_NAME),
)
USER_PERMS_NAMES = [MANAGER_NAME, ADMIN_NAME, STUDENT_NAME]

PERMS_CONSTANT_LIST = [MANAGER, ADMIN, STUDENT]
