import datetime

from utils.request_id_generator.RandomIdGenerator import RandomIdGenerator


class RequestIdGenerator(RandomIdGenerator):

    @staticmethod
    def generate_request_id(length=32):
        return '='.join([datetime.datetime.now().isoformat(), RandomIdGenerator.generate_random_id(length)])

    @staticmethod
    def get_date_from_request_id(request_id):
        request_datetime, _ = request_id.split('=')
        return datetime.datetime.strptime(request_datetime, "%Y-%m-%dT%H:%M:%S.%f")


if __name__ == '__main__':
    print(RequestIdGenerator.generate_random_id())
