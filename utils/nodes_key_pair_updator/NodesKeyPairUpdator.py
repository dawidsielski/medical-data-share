import os
import requests
import logging

from logging.handlers import TimedRotatingFileHandler
from urllib.parse import urljoin
from configparser import ConfigParser

from data_share import DataShare
from data_share.KeyGeneration import KeyGeneration
from nodes_available.NodesChecker import NodesChecker
from utils.request_id_generator.RequestIdGenerator import RequestIdGenerator

key_path = lambda name: os.path.join('keys', name)

config = ConfigParser()
config.read(os.path.join(os.getcwd(), 'config.ini'), encoding='utf-8')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(funcName)s:%(message)s')

website_file_rotating_handler = TimedRotatingFileHandler('logs/node_updates.log', when="midnight", interval=1)
website_file_rotating_handler.setLevel(logging.INFO)
website_file_rotating_handler.setFormatter(formatter)
website_file_rotating_handler.suffix = "%Y-%m-%d"

logger.addHandler(website_file_rotating_handler)


class NodeKeyPairUpdator(object):
    @staticmethod
    def rename_old_keys():
        os.rename(key_path('public.key'), key_path('public.old.key'))
        os.rename(key_path('private.key'), key_path('private.old.key'))

    @staticmethod
    def update_keys():
        NodeKeyPairUpdator().rename_old_keys()
        kg = KeyGeneration()
        kg.generate_keys()
        kg.save_keys()

        NodeKeyPairUpdator.update_key_on_available_nodes()

        os.remove(key_path('public.old.key'))
        os.remove(key_path('private.old.key'))
        logger.info('New_keys_generated')

    @staticmethod
    def update_key_on_available_nodes():
        available_nodes = NodesChecker.get_all_nodes_availability()
        logger.info(available_nodes)

        for key, value in available_nodes.items():
            if value['availability']:
                url = urljoin(value['address'], 'update-keys')

                keys = KeyGeneration()
                keys.load_keys()

                data = {
                    'node': config.get('NODE', 'LABORATORY_NAME'),
                    'public_key': keys.public_key.exportKey().decode(),
                    'request_id': RequestIdGenerator.generate_request_id(),
                }
                data.update({'signature': DataShare.get_signature_for_message(data, filename='private.old.key').decode()})

                r = requests.post(url, json=data)
                logger.info('{} {} {} {}'.format(key, url, r.status_code, data))
