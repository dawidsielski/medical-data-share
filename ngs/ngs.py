import json
import logging
import os
import datetime
import base64

from flask import Flask, render_template, redirect, url_for, jsonify, request, abort

from data_share.DataShare import DataShare

from tabix_wrapper import tabix_query
from nodes_available.NodesChecker import NODES_PATH

from configparser import ConfigParser

config = ConfigParser()
config.read(os.path.join(os.getcwd(), 'config.ini'), encoding='utf-8')

server = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(funcName)s:%(message)s')

file_handler = logging.FileHandler('logs/ngs.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


@server.route("/")
def home():
    logger.info("Runs page rendered.")
    data = {
        'lab_name': config.get('NODE', 'LABORATORY_NAME')
    }
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
        print('Data recivied: ' + json.dumps(data))
        if not DataShare.validate_signature(data):
            logger.info("Invalid signature.")
            abort(403, "Invalid signature.")

        decoded_information = DataShare.decrypt_data(data['data'])
        filename = str(datetime.datetime.now()).replace(':', "--")
        with open(os.path.join('data_acquisition', '{}.txt'.format(filename)), 'w') as incoming_data_file:
            incoming_data_file.write(decoded_information)
            logger.info("Data saved.")

        return "Successful data acquisition", 200
    abort(403)


@server.route('/sample-node', methods=['GET', 'POST'])
def sample_node():
    """
    Sample node data
    """
    path = os.path.join('keys', 'public.key')
    with open(path, 'rb') as file:
        public_key = file.read()

    response = {
        'address': '0.0.0.0',
        'name': 'Laboratory-Warsaw2',
        'public_key': DataShare.encrypt_data(base64.b64encode(public_key).decode()),
    }

    response.update({'signature': DataShare.get_signature_for_message(response)})

    return jsonify(response), 200


@server.route('/add-node', methods=['GET', 'POST'])
def add_node():
    """
    This is an endpoint which is responsible for adding other laboratory (node) to the federation.

    Performing GET request will result in 403 (unauthorized).
    Performing POST request will resutl in adding the incoming node to this computer providing the correct data in request.

    POST request must be signed. If it is not the node will not be added.
    """
    if request.method == 'POST':
        data = json.loads(request.get_json())
        if not DataShare.validate_signature(data):
            logger.info('Invalid signature add-node')
            abort(403, 'Invalid signature.')

        with open(os.path.join('nodes', '{}.json'.format(data['name'])), 'w') as file:
            json.dump(data, file)

        with open(os.path.join('nodes', '{}.key'.format(data['name'])), 'w') as file:
            file.write(base64.b64decode(DataShare.decrypt_data(data['public_key'])).decode())

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
    variants_path = os.path.join(os.getcwd(), 'data')
    genome = os.path.join(variants_path, 'gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz')

    if request.method == 'POST':
        try:
            params = request.get_json()
            genome_build = 'hg19'  # this will be hg19 or hg38
            chrom = params['chrom']
            start = params['start']
        except KeyError as e:
            logger.exception(e)
            return abort(406)

        try:
            chromosome_results = tabix_query(genome, chrom, start, start)
            response = {'result': list(chromosome_results)}
            return json.dumps(response), 200
        except Exception as e:
            logger.exception(e)
            return abort(500)


    data = {
        'lab_name': config.get('NODE', 'LABORATORY_NAME')
    }
    return render_template('public_variants.html', **data)


@server.route('/variants-private', methods=['GET', 'POST'])
def variants_private():
    variants_path = os.path.join(os.getcwd(), 'data')
    genome = os.path.join(variants_path, 'gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz')

    if request.method == 'POST':
        try:
            params = request.get_json()
            param_keys = params.keys()
            genome_build = 'hg19'  # this will be hg19 or hg38

            if 'end' in param_keys and 'start' in param_keys and 'chrom' in param_keys:
                chromosome_results = tabix_query(genome, params['chrom'], params['start'], params['end'])
            elif 'start' in param_keys and 'chrom' in param_keys:
                chromosome_results = tabix_query(genome, params['chrom'], params['start'], params['start'])
            elif 'chrom' in param_keys:
                chromosome_results = tabix_query(genome, params['chrom'])
            else:
                pass

        except KeyError as e:
            logger.exception(e)
            return abort(406)

        try:
            response = {'result': list(chromosome_results)}
            return json.dumps(response), 200
        except Exception as e:
            logger.exception(e)
            return abort(500)

    data = {
        'lab_name': config.get('NODE', 'LABORATORY_NAME')
    }
    return render_template('private_variants.html', **data)


@server.route('/nodes', methods=['GET', 'POST'])
def available_nodes():
    available_nodes_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'nodes_available', 'nodes_available.json')
    with open(available_nodes_path, 'r') as json_file:
        nodes = json.load(json_file)

    data = {
        'lab_name': config.get('NODE', 'LABORATORY_NAME')
    }
    return render_template('nodes.html', nodes=nodes, **data)
