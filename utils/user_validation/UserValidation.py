import os
import json
import requests

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
        This functin checks if user named <user_id> exists in remote node.
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

        return check_user_response

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
            return UserValidation.check_remote_node(user_id, node)['result']
