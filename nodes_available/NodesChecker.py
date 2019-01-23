import os
import requests
import json

NODES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'nodes')


class NodesChecker(object):

    @staticmethod
    def get_all_nodes():
        return [node for node in os.listdir(NODES_PATH) if node.endswith(".json")]

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
            request_address = node_information[address_key]
        except KeyError:
            return False

        try:
            return requests.get(request_address).status_code == 200
        except Exception:
            return False

    @staticmethod
    def get_all_nodes_availability(save=True):
        all_nodes = NodesChecker.get_all_nodes()

        node_availability = {}
        for node in all_nodes:
            node = NodesChecker.get_node_information(node)
            data = {
                'availability': NodesChecker.get_node_availability(node),
                'address': node['address']
            }
            node_availability[node['name']] = data

        if save:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'nodes_available.json'), 'w') as json_file:
                json.dump(node_availability, json_file)
        return node_availability
