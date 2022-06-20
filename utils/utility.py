import random
import time
from string import digits


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