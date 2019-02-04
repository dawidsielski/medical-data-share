import random
import datetime
import string


class RandomIdGenerator(object):

    @staticmethod
    def generate_random_id(length=32):
        characters = string.ascii_letters + string.digits
        random_part = ''.join(random.choice(characters) for _ in range(length))
        return random_part
