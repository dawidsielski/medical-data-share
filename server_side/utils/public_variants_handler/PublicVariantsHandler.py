import os
import json


from configparser import ConfigParser

config = ConfigParser()
config.read(os.path.join(os.getcwd(), 'config.ini'), encoding='utf-8')


class PublicVariantsHandler(object):

    @staticmethod
    def get_limit_from_config():
        return config.getint('NODE', 'MAX_PUBLIC_VARIANT_REQUEST_LIMIT')

    @staticmethod
    def create_temp_file():
        data = {'public_variants_requests_left': PublicVariantsHandler.get_limit_from_config()}
        with open('temp.json', 'w') as file:
            json.dump(data, file)

    @staticmethod
    def reset_limit():
        with open('temp.json', 'r') as file:
            data = json.load(file)

        data['public_variants_requests_left'] = PublicVariantsHandler.get_limit_from_config()

        with open('temp.json', 'w') as file:
            json.dump(data, file)

    @staticmethod
    def get_temp():
        with open('temp.json', 'r') as file:
            data = json.load(file)
        return data

    @staticmethod
    def get_limit_left():
        data = PublicVariantsHandler.get_temp()
        return data['public_variants_requests_left']

    @staticmethod
    def decrease_number_of_requests_left(value=1):
        current = PublicVariantsHandler.get_limit_left()

        data = {'public_variants_requests_left': current - value}
        with open('temp.json', 'w') as file:
            json.dump(data, file)
