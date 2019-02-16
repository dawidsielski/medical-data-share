import os
import requests
import json

from data_share import DataShare
from utils.request_id_generator.RequestIdGenerator import RequestIdGenerator

from configparser import ConfigParser
from urllib.parse import urljoin

NODES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'nodes')

config = ConfigParser()
config.read(os.path.join(os.getcwd(), 'config.ini'), encoding='utf-8')


class NodesChecker(object):

    @staticmethod
    def get_all_nodes():
        """
        This function will get all nodes minus host node.
        :return: (list)
        """
        this_node = config.get('NODE', 'LABORATORY_NAME')
        return [node for node in os.listdir(NODES_PATH) if node.endswith(".json") and not node.startswith(this_node)]

    @staticmethod
    def get_node_information(node_name):
        """
        This function returns information about the node given by its name
        :param node_name: (str) laboratory name
        :return: (dict) information about the node.
        """
        with open(os.path.join(NODES_PATH, node_name)) as f:
            node_information = json.load(f)
        return node_information

    @staticmethod
    def get_node_availability(node_information, address_key='address'):
        """
        This function checks if specific node is available.
        :param node_information: (dict)
        :param address_key: (str) default 'address' holds key value for address
        :return: (bool) says if node is available for data sharing
        """
        try:
            request_address = urljoin(node_information[address_key], 'check-node')
        except KeyError:
            return False

        try:
            data = {
                'request_node': config.get('NODE', 'LABORATORY_NAME'),
                'request_id': RequestIdGenerator.generate_random_id()
            }
            data.update({'signature': DataShare.get_signature_for_message(data).decode()})
            return requests.get(request_address, json=data).status_code == 200
        except Exception:
            return False

    @staticmethod
    def get_all_nodes_availability():
        """
        This function will check availability of all nodes and save this information to a file.
        :return: (dict) nodes availability information
        """
        all_nodes = NodesChecker.get_all_nodes()

        node_availability = {}
        for node in all_nodes:
            node = NodesChecker.get_node_information(node)
            data = {
                'availability': NodesChecker.get_node_availability(node),
                'address': node['address']
            }
            node_availability[node['laboratory-name']] = data

        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'nodes_available.json'), 'w') as json_file:
            json.dump(node_availability, json_file)

        return node_availability
