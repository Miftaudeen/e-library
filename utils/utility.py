import random
import time
from datetime import datetime
from string import digits

import library


def generate_digits(length):
    code = ""
    for i in range(length):
        code += random.choice(digits)
    return code


def generate_reference_time_id():
    token_x = str(time.time()).replace('.', '')
    return str(token_x)


def generate_username(first_name, last_name, more=False):
    username = f'{first_name[0]}{last_name}'
    if more:
        random_number = '{:02d}'.format(random.randrange(1, 99))
        username = f'{username}{random_number}'
    return username.lower().replace(" ", "")


def generate_matric_num(inc=0):
    initials = datetime.now().year
    students = library.models.Student.objects.all().order_by("matric_num")
    if students.exists():
        last_matric_num = students.last().code.split('-')[-1]
        new_matrc_num = f"{initials}-{str(int(last_matric_num) + 1 + inc).zfill(6)}"
        prev = library.models.Student.objects.filter(code=new_matrc_num)
        if prev.exists():
            inc += 1
            return generate_matric_num(inc=inc)
        return new_matrc_num
    return f"{initials}-000001"
