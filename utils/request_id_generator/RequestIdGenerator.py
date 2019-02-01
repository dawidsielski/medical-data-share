import random
import datetime
import string


class RequestIdGenerator(object):

    @staticmethod
    def generate_random_id(length=32):
        characters = string.ascii_letters + string.digits
        random_part = ''.join(random.choice(characters) for _ in range(length))
        return '='.join([datetime.datetime.now().isoformat(), random_part])

    @staticmethod
    def get_date_from_request_id(request_id):
        request_datetime, _ = request_id.split('=')
        return datetime.datetime.strptime(request_datetime, "%Y-%m-%dT%H:%M:%S.%f")
