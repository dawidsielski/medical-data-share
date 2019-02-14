import os
import json
import requests
import datetime

from urllib.parse import urljoin
from configparser import ConfigParser

import data_share
from utils.request_id_generator.RequestIdGenerator import RequestIdGenerator

config = ConfigParser()
config.read(os.path.join(os.getcwd(), 'config.ini'), encoding='utf-8')


class UserValidation(object):

    @staticmethod
    def check_local_users(user_id, node):
        """
        This function validates local user.
        :param user_id: (str) 32 character random user identification string
        :param node: (str) node to which the user belongs to
        :return: public_key (str) if user exists, None there is no such user
        """
        try:
            with open(os.path.join('public_keys', 'public.{}@{}.key'.format(user_id, node)), 'r') as file:
                public_key = file.read()
        except FileNotFoundError:
            public_key = False

        if UserValidation.key_expired('{}@{}'.format(user_id, node)):
            return False

        return public_key

    @staticmethod
    def get_node_address(node):
        """
        This function returns the address of the node. It returns False if there is no such node.
        :param node: (str) node (laboratory) name
        :return: (str) node address or (bool) False if there is no such node
        """
        nodes_available_path = os.path.join('nodes_available', 'nodes_available.json')

        with open(nodes_available_path, 'r') as file:
            nodes = json.load(file)

        return nodes[node]['address'] if node in nodes.keys() else False

    @staticmethod
    def check_remote_node(user_id, node):
        """
        This function checks if user named <user_id> exists in remote node.
        :param user_id: (str) user identification string
        :param node: (str) the name of the node
        :return: (dict) user authorization information
        """
        node_address = UserValidation.get_node_address(node)

        if not node_address:
            return False

        post_json = {
            'user_id': user_id,
            'node': node,
            'request_node': config.get('NODE', 'LABORATORY_NAME'),
            'request_id': RequestIdGenerator.generate_request_id()
        }
        post_json = dict(sorted(post_json.items()))
        post_json.update({'signature': data_share.DataShare.get_signature_for_message(post_json).decode()})

        check_user_request = requests.post(urljoin(node_address, 'check-user'), json=post_json)

        if check_user_request.status_code is not 200:
            return False

        check_user_response = check_user_request.json()

        with open(os.path.join('nodes', 'public.{}.key'.format(node)), 'r') as file:
            public_key = file.read()

        if not data_share.DataShare.validate_signature_from_message(check_user_response, public_key=public_key):
            return False

        return check_user_response['result']

    @staticmethod
    def validate_user(user_id):
        """
        This function checks if user_id is authorized to access the data.
        :param user_id: (str) user identification string
        :return: dict if user is authorized and False if not
        """
        user_id, node = user_id.split('@')
        if node == config.get('NODE', 'LABORATORY_NAME'):
            return UserValidation.check_local_users(user_id, node)
        else:
            return UserValidation.check_remote_node(user_id, node)

    @staticmethod
    def check_key_expiration_date():
        expiration_dates_file = os.path.join('utils', 'user_validation', 'expiration_dates.json')

        if not os.path.isfile(expiration_dates_file):
            with open(expiration_dates_file, 'w') as file:
                json.dump({}, file)

        with open(expiration_dates_file, 'r') as file:
            expiration_dates = json.load(file)

        existing_expiration_dates = set(expiration_dates.keys())
        existing_files = set([x[7:-4] for x in os.listdir('public_keys')])

        new_keys = existing_files - existing_expiration_dates

        for user_id in list(new_keys):
            expiration_dates[user_id] = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()

        with open(expiration_dates_file, 'w') as file:
            json.dump(expiration_dates, file)

    @staticmethod
    def key_expired(user_id):
        expiration_dates_file = os.path.join('utils', 'user_validation', 'expiration_dates.json')

        with open(expiration_dates_file, 'r') as file:
            expiration_dates = json.load(file)

        user_expiration_date = expiration_dates[user_id]

        return datetime.datetime.strptime(user_expiration_date, '%Y-%m-%d').date() < datetime.date.today()

    @staticmethod
    def update_expiration_key_date(user_id):
        expiration_dates_file = os.path.join('utils', 'user_validation', 'expiration_dates.json')

        with open(expiration_dates_file, 'r') as file:
            expiration_dates = json.load(file)

        expiration_dates[user_id] = datetime.datetime.strptime(expiration_dates[user_id], '%Y-%m-%d').date() + datetime.timedelta(days=30)

        with open(expiration_dates_file, 'w') as file:
            json.dump(expiration_dates, file)
