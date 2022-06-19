import random


def generate_username(first_name, last_name, more=False):
    username = f'{first_name[0]}{last_name}'
    if more:
        random_number = '{:02d}'.format(random.randrange(1, 99))
        username = f'{username}{random_number}'
    return username.lower().replace(" ", "")