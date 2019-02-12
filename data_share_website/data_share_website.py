import json
import logging
import os
import datetime
import re

from logging.handlers import TimedRotatingFileHandler
from configparser import ConfigParser
from flask import Flask, render_template, redirect, url_for, jsonify, request, abort

from data_share.DataShare import DataShare
from data_share.KeyGeneration import KeyGeneration
from variant_db.TabixedTableVarinatDB import TabixedTableVarinatDB
from utils.public_variants_handler.PublicVariantsHandler import PublicVariantsHandler
from utils.request_id_generator.RequestIdGenerator import RequestIdGenerator
from utils.encryption_key_generator.EncryptionKeyGenerator import EncryptionKeyGenerator
from utils.user_validation.UserValidation import UserValidation

config = ConfigParser()
config.read(os.path.join(os.getcwd(), 'config.ini'), encoding='utf-8')

server = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(funcName)s:%(message)s')

website_file_rotating_handler = TimedRotatingFileHandler('logs/website/data_haring_website.log', when="midnight", interval=1)
website_file_rotating_handler.setLevel(logging.INFO)
website_file_rotating_handler.setFormatter(formatter)
website_file_rotating_handler.suffix = "%Y-%m-%d"

logger.addHandler(website_file_rotating_handler)

data_sharing_logger = logging.getLogger('data_sharing')
data_sharing_logger.setLevel(logging.INFO)

data_sharing_file_rotating_handler = TimedRotatingFileHandler('logs/data_sharing/data_sharing.log', when="midnight", interval=1)
data_sharing_file_rotating_handler.setLevel(logging.INFO)
data_sharing_file_rotating_handler.setFormatter(formatter)
data_sharing_file_rotating_handler.suffix = "%Y-%m-%d"
data_sharing_logger.addHandler(data_sharing_file_rotating_handler)


@server.route("/")
def home():
    data = {
        'lab_name': config.get('NODE', 'LABORATORY_NAME')
    }
    logger.info("Home page rendered.")
    return render_template('index.html', **data)


@server.errorhandler(404)
def page_not_found(error):
    """
    This function renders 404 page.
    """
    logger.error('Page not found.')
    data = {
        'lab_name': config.get('NODE', 'LABORATORY_NAME')
    }
    return render_template('page_not_found.html', **data), 404


@server.route("/sample-data")
def send_data():
    """
    Sample data to be send.
    """
    encrypted = DataShare.encrypt_data("The message sdfsdlksjflksjflsdkj.")
    # response keys must be sorted
    response = {
        "data": encrypted,
        "name": 'Laboratory-Warsaw',
    }
    print('Data send: ' + json.dumps(response))

    response.update({'signature': DataShare.get_signature_for_message(response)})

    return jsonify(response), 200


@server.route("/data", methods=['GET', 'POST'])
def receive_data():
    """
    This is an endpoint responsible for sharing the data.

    Performing GET request will result in 403 (unauthorized).
    Performing POST request will result in sharing the data and saving them into `data_acquisition` folder.

    POST request must be signed. If it is not the node will not be added.
    """
    if request.method == 'POST':
        data = json.loads(request.get_json())
        print('Data received: ' + json.dumps(data))
        if not DataShare.validate_signature_from_message(data):
            logger.info("Invalid signature.")
            abort(403, "Invalid signature.")

        decoded_information = DataShare.decrypt_data(data['data'])
        filename = str(datetime.datetime.now()).replace(':', "--")
        with open(os.path.join('data_acquisition', '{}.txt'.format(filename)), 'w') as incoming_data_file:
            incoming_data_file.write(decoded_information)
            logger.info("Data saved.")

        return "Successful data acquisition", 200
    abort(403)


@server.route('/add-node', methods=['GET', 'POST'])
def add_node():
    """
    This is an endpoint which is responsible for adding other laboratory (node) to the federation.

    Performing GET request will result in 403 (unauthorized).
    Performing POST request will result in adding the incoming node to this computer providing the correct data in request.

    POST request must be signed. If it is not the node will not be added.
    """
    if request.method == 'POST':
        data = request.get_json()
        try:
            if not DataShare.validate_signature_using_user_id(data):
                data_sharing_logger.info("Invalid signature. User id:{}".format(data['user_id']))
                abort(403, "Invalid signature.")
        except KeyError:
            data_sharing_logger.info("Signature not provided.")
            abort(406, "Invalid data supplied. User id:{}".format(data['user_id']))
        except FileNotFoundError:
            data_sharing_logger.info("No public key supports this request.")
            abort(400)

        data_sharing_logger.info('Add node: {}'.format(data))

        with open(os.path.join('nodes', '{}.json'.format(data['laboratory-name'])), 'w') as file:
            json.dump(data, file)

        with open(os.path.join('nodes', 'public.{}.key'.format(data['laboratory-name'])), 'w') as file:
            file.writelines(data['public-key'])

        return 'Success', 200
    abort(403)


@server.route('/variants', methods=['GET', 'POST'])
def variants_public():
    """
    This is an public variants download api that will return variants for a given chromosome from start to end position.

    As a GET request is presents a website how to use this endpoing.

    As a POST request is returns information about variants asked in the POST request data.
    POST arguments:
        genome_build (str): information about the genome build (hg19 or hg38)
        chr (str): chromosome number
        start (str): starting point
        end (str): end point

    Having bad post arguments will result in 406 status code.
    Having problems with running tabix will result in 500 internal error status code.
    """
    if request.method == 'POST':
        if PublicVariantsHandler.get_limit_left() <= 0:
            logger.info("Public request reached.")
            abort(400, 'Limit reached.')

        try:
            params = request.get_json()
            genome_build = 'hg19'  # this will be hg19 or hg38

            if 'query' in params:
                pattern = re.compile(r'(?P<CHROM>(\d+))[ :](?P<START>(\d+))([ :](?P<STOP>\d+))?')
                s = re.search(pattern, params['query'])
                chrom, start = int(s.group('CHROM')), int(s.group('START'))
            else:
                chrom = params['chrom']
                start = params['start']
        except KeyError as e:
            logger.exception(e)
            return abort(406)
        except TypeError as e:
            logger.exception(e)
            return abort(406, 'Invalid type or data not supplied.')
        except AttributeError as e:
            logger.exception(e)
            return abort(406, 'Invalid type or data not supplied.')
        except Exception as e:
            logger.exception(e)
            return abort(500)

        try:
            chromosome_results = TabixedTableVarinatDB.get_variants(chrom, start, start)
            response = {
                'request_id': RequestIdGenerator.generate_random_id(),
                'lab_name': config.get('NODE', 'LABORATORY_NAME'),
                'result': list(chromosome_results)
            }
            PublicVariantsHandler.decrease_number_of_requests_left()
            data_sharing_logger.info('{} - {}'.format(response['request_id'], params))
            return json.dumps(response), 200
        except Exception as e:
            logger.exception(e)
            return abort(500)

    data = {
        'lab_name': config.get('NODE', 'LABORATORY_NAME'),
        'current_limit': PublicVariantsHandler.get_limit_left()
    }
    logger.info('Variants public page')
    return render_template('public_variants.html', **data)


@server.route('/variants-private', methods=['GET', 'POST'])
def variants_private():
    """
    This is a private variant download api that will return variants depending on a given query.

    As a GET request is presents a website how to use this endpoint.

    As a POST request is returns information about variants asked in the POST request data.
    POST arguments:
        genome_build (str): information about the genome build (hg19 or hg38)
        chr (str): chromosome number
        start (str): starting point
        end (str): end point
        signature (str): TODO

    Having bad post arguments will result in 406 status code.
    Having problems with running tabix will result in 500 internal error status code.
    """
    if request.method == 'POST':
        params = request.get_json()
        try:
            valid_signature, public_key = DataShare.validate_signature(params)
            if not valid_signature:
                data_sharing_logger.info("Invalid signature. User id:{}".format(params['user_id']))
                abort(403, "Invalid signature.")
        except KeyError:
            data_sharing_logger.info("Signature not provided.")
            abort(406, "Invalid data supplied. User id:{}".format(params['user_id']))
        except FileNotFoundError:
            data_sharing_logger.info("No public key supports this request.")
            abort(400)

        try:
            param_keys = params.keys()
            genome_build = 'hg19'  # this will be hg19 or hg38

            if 'end' in param_keys and 'start' in param_keys and 'chrom' in param_keys:
                chromosome_results = TabixedTableVarinatDB.get_variants(params['chrom'], params['start'], params['end'])
            elif 'start' in param_keys and 'chrom' in param_keys:
                chromosome_results = TabixedTableVarinatDB.get_variants(params['chrom'], params['start'], params['start'])
            elif 'chrom' in param_keys:
                chromosome_results = TabixedTableVarinatDB.get_variants(params['chrom'])
            else:
                chromosome_results = []

        except KeyError as e:
            data_sharing_logger.exception(e)
            return abort(406)
        except TypeError as e:
            data_sharing_logger.exception(e)
            return abort(406, 'Invalid type or data not supplied.')

        try:
            _new_encryption_key = EncryptionKeyGenerator().generate_encryption_key()
            data_sharing_logger.debug('Encryption key: {}'.format(_new_encryption_key))

            response = {
                'request_id': RequestIdGenerator.generate_random_id(),
                'lab_name': config.get('NODE', 'LABORATORY_NAME'),
                'encryption_key': DataShare.encrypt_using_public_key(_new_encryption_key, params['user_id'], public_key),
                'result': DataShare.encrypt_data(json.dumps(list(chromosome_results)), _new_encryption_key)
            }
            data_sharing_logger.info('{} - {}'.format(response['request_id'], params))
            return json.dumps(response), 200
        except Exception as e:
            data_sharing_logger.exception(e)
            return abort(500)

    data = {
        'lab_name': config.get('NODE', 'LABORATORY_NAME')
    }
    logger.info("Private variants rendered")
    return render_template('private_variants.html', **data)


def get_all_nodes_info():
    nodes_path = os.path.join('nodes')
    nodes = [node for node in os.listdir(nodes_path) if node.endswith('.json')]
    my_keys = ['address', 'public-key', 'laboratory-name']

    nodes_information = []
    for node_path in [os.path.join(nodes_path, node) for node in nodes]:
        try:
            with open(node_path, 'r') as file:
                node_info = json.load(file)
        except json.decoder.JSONDecodeError as e:
            logger.exception(e)
            continue

        nodes_information.append({key: node_info[key] for key in my_keys})

    my_lab_name = config.get('NODE', 'LABORATORY_NAME')
    my_lab_address = config.get('NODE', 'NODE_ADDRESS')
    keys = KeyGeneration()
    keys.load_keys()
    my_public_key = keys.public_key.exportKey().decode()
    nodes_information.append({'address': my_lab_address, 'public-key': my_public_key, 'laboratory-name': my_lab_name})
    return nodes_information


@server.route('/nodes', methods=['GET', 'POST'])
def available_nodes():
    """
    As a get request this function renders /nodes webpage on which nodes that are available are presented.

    As a post request this function will return information about all available nodes.
    """
    available_nodes_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'nodes_available', 'nodes_available.json')

    try:
        with open(available_nodes_path, 'r') as json_file:
            nodes = json.load(json_file)
    except FileNotFoundError:
        logger.exception('Nodes available not found.')
        nodes = {}

    if request.method == 'POST':
        return jsonify(get_all_nodes_info())

    data = {
        'lab_name': config.get('NODE', 'LABORATORY_NAME')
    }
    return render_template('nodes.html', nodes=nodes, **data)


@server.route('/check-user', methods=['GET', 'POST'])
def check_user():
    """
    As a get request this function will give 400 bad request status code.

    As a post request this function will check if given user is authorized to get the data from server.
    """
    if request.method == 'POST':
        data = request.json

        try:
            with open(os.path.join('nodes', 'public.{}.key'.format(data['request_node'])), 'r') as file:
                public_key = file.read()
        except FileNotFoundError as e:
            data_sharing_logger.exception("Remote user check failed. Request: {}".format(data))
            data_sharing_logger.exception(e)
            abort(403)

        if not DataShare.validate_signature_from_message(data, public_key=public_key):
            abort(403)

        result = {
            'request_id': RequestIdGenerator.generate_request_id(),
            'result': UserValidation.check_local_users(data['user_id'], data['node']),
        }
        result = dict(sorted(result.items()))
        result.update({'signature': DataShare.get_signature_for_message(result).decode()})
        data_sharing_logger.info("Remote user check. {}".format(result))
        return jsonify(result)

    abort(400)
