import os
import json
import requests

from urllib.parse import urljoin
from configparser import ConfigParser

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
            'node': node
        }

        check_user_request = requests.post(urljoin(node_address, 'check-user'), json=post_json)
        check_user_response = check_user_request.json()
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
            return UserValidation.check_remote_node(user_id, node)
