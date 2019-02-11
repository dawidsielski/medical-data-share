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
        THis function valides local user.
        :param user_id: (str) 32 character random user identification string
        :param node: (str) node to which the user belongs to
        :return: (bool) True is user_id is valid for this node, False if user is not valid for this node
        """
        users_path = os.path.join('public_keys')
        user_id_path = os.path.join(users_path, 'public.{}@{}.key'.format(user_id, node))
        return os.path.isfile(user_id_path)

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
        node_address = UserValidation.get_node_address(node)

        if not node_address:
            return False

        post_json = {
            'user_id': user_id,
            'node': node
        }

        check_user_request = requests.post(urljoin(node_address, 'check-user'), json=post_json)
        check_user_response = check_user_request.json()
        return check_user_response['result']

    @staticmethod
    def validate_user(user_id):
        user_id, node = user_id.split('@')
        if node == config.get('NODE', 'LABORATORY_NAME'):
            return UserValidation.check_local_users(user_id, node)
        else:
            return UserValidation.check_remote_node(user_id, node)
