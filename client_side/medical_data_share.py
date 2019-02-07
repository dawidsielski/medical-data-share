import requests
import argparse
import json
import os
import sys
import re

from data_share.DataShare import DataShare
from data_share.KeyGeneration import KeyGeneration
from utils.PublicKeyPreparation import PublicKeyPreparation


def prepare_public_request(chrom=None, start=None, end=None):
    data = {
        'chrom': chrom,
        'start': start,
        'end': end
    }
    return data


def data_request_public(endpoint, chrom=None, start=None, end=None):
    data = prepare_public_request(chrom, start, end)
    return requests.post(endpoint, json=data)


def data_request(endpoint, chrom=None, start=None, end=None):
    data = prepare_public_request(chrom, start, end)
    data.update({'user_id': PublicKeyPreparation.get_user_id()})
    data = dict(sorted(data.items()))
    data.update({'signature': DataShare.get_signature_for_message(data).decode()})
    return requests.post(endpoint, json=data)


def handle_request(r, args):
    if r.status_code == 200:
        obtained_data = json.loads(r.text)

        if args.raw:
            print('Raw response:')
            print(obtained_data)

        if 'encryption_key' in obtained_data:
            obtained_data['result'] = decrypt_result(obtained_data)
            obtained_data.pop('encryption_key')

        if args.save:
            with open('{}.json'.format(obtained_data['request_id']), 'w') as file:
                json.dump(obtained_data, file)
            print('File has been saved.')

        if args.verbose:
            print('Query result (after decryption):')
            print(obtained_data['result'])
    else:
        print(r.status_code)
        print(r.text)


def handle_keys_generation():
    if os.listdir('keys'):
        choice = input("Keys are generated. Do you want to generate new ones? [y or n](default n)")
        if choice in ['n', 'N', 'NO', 'No']:
            print("No keys generated.")
            sys.exit(0)
        elif choice in ['y', 'Y', 'YES', 'Yes']:
            print("New keys generated.")
            pass
        else:
            print("Wrong input. Try again.")
            sys.exit(0)

    keys = KeyGeneration()
    keys.load_or_generate()
    PublicKeyPreparation.prepare_public_key()


def get_params_from_query(query):
    pattern = re.compile(r'(?P<CHROM>(\d+))[ :](?P<START>(\d+))([ :](?P<STOP>\d+))?')
    s = re.search(pattern, query)
    return int(s.group('CHROM')), int(s.group('START'))


def decrypt_result(message):
    encryption_key = bytes.fromhex(message['encryption_key'])
    encryption_key = DataShare.decrypt_using_private_key(encryption_key)
    decrypted_data = json.loads(DataShare.decrypt_data(message['result'], encryption_key))
    return decrypted_data


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--generate', action='store_true', help='Generates public and private key together with user id.')

    parser.add_argument('-e', '--endpoint', help='Endpoint to which request is performed.', default="")
    parser.add_argument('-q', '--query', type=str)
    parser.add_argument('-ch', '--chrom', type=int, help='Chromosome number.')
    parser.add_argument('--start', type=int, help='Starting position.')
    parser.add_argument('--stop', type=int, help='Ending position.')

    parser.add_argument('-s', '--save', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true', default=True)
    parser.add_argument('-r', '--raw', action='store_true', help='Will print raw response.')

    args = parser.parse_args()
    print(args)

    if args.endpoint.endswith('variants'):
        if args.chrom and args.start:
            r = data_request_public(args.endpoint, args.chrom, args.start)
            handle_request(r, args)
        elif args.query:
            chrom, start = get_params_from_query(args.query)
            r = data_request_public(args.endpoint, chrom, start)
            handle_request(r, args)
    elif args.endpoint.endswith('variants-private'):
        r = data_request(args.endpoint, args.chrom, args.start, args.stop)
        message = json.loads(r.text)
        handle_request(r, args)

    elif args.generate:
        handle_keys_generation()
