import os
import json
import requests
import urllib


NODES_PATH = os.path.join('..', 'nodes')


class Node(object):

    def __init__(self, ip_address=None, name=None, public_key=None):
        self.ip_address = ip_address
        self.name = name
        self.public_key = public_key

    def __str__(self):
        return '{} {}'.format(self.name, self.ip_address)

    @staticmethod
    def get_all_nodes():
        return [node.split('.')[0] for node in os.listdir(NODES_PATH) if node.endswith(".json")]

    def load_node_information(self, lab_name):
        if lab_name not in Node.get_all_nodes():
            raise NameError("There is no laboratory with this name")

        with open(os.path.join(NODES_PATH, '{}.json'.format(lab_name))) as file:
            laboratory_informations = json.load(file)

        self.ip_address = laboratory_informations['address']
        self.name = laboratory_informations['name']
        self.public_key = laboratory_informations['public_key']

    def get_node_status(self):
        url = urllib.parse.urlunparse(('http', '{}'.format(self.ip_address), '/', None, '', ''))
        print(url)
        return requests.get(url).status_code


if __name__ == '__main__':
    n = Node()
    print(n.get_all_nodes())
    n.load_node_information(n.get_all_nodes()[0])
    n.ip_address = '127.0.0.1:5000'
    print(n.get_node_status())
