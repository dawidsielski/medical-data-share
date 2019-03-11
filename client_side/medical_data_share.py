import requests
import argparse
import json
import os
import sys
import re
import datetime

from pprint import pprint
from urllib.parse import urlparse, urljoin

from data_share.DataShare import DataShare
from data_share.KeyGeneration import KeyGeneration
from utils.PublicKeyPreparation import PublicKeyPreparation


def prepare_public_request(chrom=None, start=None, end=None, genome_build=None):
    data = {
        'chrom': chrom,
        'genome_build': genome_build,
        'start': start,
        'end': end
    }
    return data


def data_request_public(endpoint, genome_build, chrom=None, start=None, end=None):
    data = prepare_public_request(chrom, start, end, genome_build)
    return requests.post(endpoint, json=data)


def data_request(endpoint, genome_build, chrom=None, start=None, end=None):
    data = prepare_public_request(chrom, start, end, genome_build)
    data.update({'user_id': PublicKeyPreparation.get_user_id()})
    data.update({'signature': DataShare.get_signature_for_message(data).decode()})
    return requests.post(endpoint, json=data)


def handle_request(r, args):
    if r.status_code == 200:
        obtained_data = json.loads(r.text)

        if args.raw:
            print('Raw response:')
            pprint(obtained_data)

        if 'encryption_key' in obtained_data:
            obtained_data['result'] = decrypt_result(obtained_data)
            obtained_data.pop('encryption_key')

        if args.save:
            with open('{}.json'.format(obtained_data['request_id']), 'w') as file:
                json.dump(obtained_data, file)
            print('File has been saved.')

        if args.verbose:
            print('Query result (after decryption):')
            pprint(obtained_data['result'], width=300)
    else:
        print(r.status_code)
        pprint(r.text)


def handle_keys_generation():
    if os.path.isdir('keys'):
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
    else:
        os.mkdir('keys')

    keys = KeyGeneration()
    keys.load_or_generate()
    PublicKeyPreparation.prepare_public_key()

    # os.rename(os.path.join('keys', 'public.key'), os.path.join('keys', public_name))


def get_params_from_query(query):
    pattern = re.compile(r'(?P<CHROM>(\d+))[ :](?P<START>(\d+))([ :](?P<STOP>\d+))?')
    s = re.search(pattern, query)
    return int(s.group('CHROM')), int(s.group('START'))


def decrypt_result(message):
    encryption_key = bytes.fromhex(message['encryption_key'])
    encryption_key = DataShare.decrypt_using_private_key(encryption_key)
    decrypted_data = json.loads(DataShare.decrypt_data(message['result'], encryption_key))
    return decrypted_data


def get_user_id():
    with open('keys/user_id', 'r') as file:
        user_id = file.read()
    return user_id


def load_public_key_for_sending(public_key_path):
    with open(public_key_path, 'r') as file:
        public_key = file.read()
    return public_key


def add_node(endpoint, public_key_path, node_address, lab_name):
    public_key = load_public_key_for_sending(public_key_path)
    data = {
        'laboratory-name': lab_name,
        'public-key': public_key,
        'address': node_address,
        'user_id': get_user_id()
    }
    data = dict(sorted(data.items()))
    data.update({'signature': DataShare.get_signature_for_message(data).decode()})

    parsed_uri = urlparse(endpoint)
    result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    all_nodes = requests.post(urljoin(result, 'nodes')).json()

    add_node_endpoint = lambda x: urljoin(x, 'add-node')

    print('Adding {} laboratory at {} to every node.'.format(lab_name, node_address))
    r = requests.post(endpoint, json=data)
    for node in all_nodes:

        if node['laboratory-name'] == data['laboratory-name']:
            continue

        add_node_specific_endpoint = add_node_endpoint(node['address'])
        try:
            r = requests.post(add_node_specific_endpoint, json=data)
            print('Adding node for {} at {} with {} status_code'.format(node['laboratory-name'], node['address'], r.status_code))
            print(r.text)
        except Exception as e:
            print(e)
            print('Error in adding node to {} at {} '.format(node['laboratory-name'], node['address']))


def get_nodes(args):
    available_laboratories = requests.post(args.endpoint).json()
    print('There are {} laboratories available.'.format(len(available_laboratories)))

    if args.verbose:
        pprint(available_laboratories)
    else:
        print('If you want to print the result please specify -v flag.')

    if args.save:
        print('Saving to /nodes folder.')
        if not os.path.isdir('nodes'):
            os.mkdir('nodes')
        for lab in available_laboratories:
            name = lab['laboratory-name']
            print('Saving {} laboratory.'.format(name))

            with open(os.path.join('nodes', '{}.json'.format(name)), 'w') as file:
                json.dump(lab, file)

            with open(os.path.join('nodes', 'public.{}.key'.format(name)), 'w') as file:
                file.writelines(lab['public-key'])

        print('All nodes saved.')
    else:
        print('If you want to save the result please specify -s flag.')


def variants_from_all_nodes(args, private=False):
    available_laboratories = requests.post(urljoin(args.endpoint, 'nodes')).json()

    result, data = {}, []
    for lab in available_laboratories[::-1]:
        print('Getting information from \"{}\" laboratory.'.format(lab['laboratory-name']))

        if private:
            endpoint = urljoin(lab['address'], 'variants-private')
        else:
            endpoint = urljoin(lab['address'], 'variants')
        r = data_request(endpoint, args.genome_build, args.chrom, args.start, args.stop)

        try:
            obtained_data = r.json()
        except Exception:
            print('ERROR from \"{}\" laboratory.'.format(lab['laboratory-name']))
            continue

        if 'encryption_key' in obtained_data:
            obtained_data['result'] = decrypt_result(obtained_data)
            obtained_data.pop('encryption_key')

        data.append(obtained_data)

    result = {
        'chromosome': args.chrom,
        'start': args.start,
        'stop': args.stop,
        'request_time': datetime.datetime.now().isoformat(),
        'result': data
    }

    if args.verbose:
        pprint(result)

    if args.save:
        filename = 'all_chr_{}_start_stop_{}.json'.format(args.chrom, args.start, args.stop)
        print('Saving to json file called {}'.format(filename))

        with open(filename, 'w') as file:
            json.dump(result, file)

        print('Successfully saved.')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--generate', action='store_true', help='Generates public and private key together with user id.')

    parser.add_argument('-e', '--endpoint', help='Endpoint to which request is performed.', default="")
    parser.add_argument('-q', '--query', type=str)
    parser.add_argument('-ch', '--chrom', type=int, help='Chromosome number.')
    parser.add_argument('--start', type=int, help='Starting position.')
    parser.add_argument('--stop', type=int, help='Ending position.')
    parser.add_argument('-gb', '--genome-build', type=str, help='Holds information about gemone build.', default='hg19')

    parser.add_argument('-a', '--all-nodes', action='store_true', help='This flag will aggregate data form all available nodes.')
    parser.add_argument('-k', '--key', type=str, help='Path to a public key file.')
    parser.add_argument('-ln', '--lab-name', type=str, help='Full laboratory name (as in config file)')
    parser.add_argument('-la', '--lab-address', type=str, help='This is a laboratory address (e.g. ')

    parser.add_argument('-s', '--save', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-r', '--raw', action='store_true', help='Will print raw response.')

    parser.add_argument('-ck', '--check-key', action='store_true', help="Will check your key")
    parser.add_argument('-uk', '--update-user-key', action='store_true', help="Will update your key")

    args = parser.parse_args()

    if not args.verbose:
        print('If you want to see the output please set -v option.')
        print('If you want to see raw output please set -r option.')
        print("---------------------------------------------------")
        print("For more help please visit -> https://github.com/dawidsielski/medical-data-share/blob/master/client_side/README.md")
        print("---------------------------------------------------")

    if args.endpoint.endswith('variants') and args.all_nodes:
        variants_from_all_nodes(args)

    elif args.endpoint.endswith('variants'):
        if (args.chrom and args.start) or (args.chrom and args.start and args.stop):
            if args.stop:
                print('Warning! Results will be presented only at position equal to start (stop position will not be used).')
            r = data_request_public(args.endpoint, args.genome_build, args.chrom, args.start)
            handle_request(r, args)
        elif args.query:
            chrom, start = get_params_from_query(args.query)
            r = data_request_public(args.endpoint, args.genome_build, chrom, start)
            handle_request(r, args)

    elif args.endpoint.endswith('variants-private') and args.all_nodes:
        variants_from_all_nodes(args, private=True)

    elif args.endpoint.endswith('variants-private'):
        r = data_request(args.endpoint, args.genome_build, args.chrom, args.start, args.stop)
        if r.status_code == 200:
            message = json.loads(r.text)
            handle_request(r, args)
        else:
            print(r.text)

    elif args.endpoint.endswith('add-node'):
        add_node(args.endpoint, args.key, args.lab_address, args.lab_name)

    elif args.generate:
        handle_keys_generation()

    elif args.endpoint.endswith('nodes'):
        print('Getting available nodes.')
        get_nodes(args)

    elif args.check_key:
        data = {
            'user_id': get_user_id()
        }
        data.update({'signature': DataShare.get_signature_for_message(data).decode()})

        r = requests.post(urljoin(args.endpoint, 'check-key'), json=data)

        if not r.json():
            print('Your key is authorized to perform private queries.')
        else:
            print('You are not authorized to perform private operations or your key has expired.')

    elif args.update_user_key:
        username = PublicKeyPreparation.get_user_id()
        old_public_name = 'public.old.{}.key'.format(username)
        public_name = 'public.{}.key'.format(username)
        os.rename(os.path.join('keys', public_name), os.path.join('keys', old_public_name))
        os.rename(os.path.join('keys', 'private.key'), os.path.join('keys', 'private.old.key'))

        keys = KeyGeneration()
        keys.load_or_generate()

        os.rename(os.path.join('keys', 'public.key'), os.path.join('keys', public_name))

        with open(os.path.join('keys', 'user_id'), 'w') as file:
            file.write(username)

        data = {
            'user_id': username,
            'public_key': keys.public_key.exportKey().decode(),
        }
        data = dict(sorted(data.items()))
        data.update({'signature': DataShare.get_signature_for_message(data, 'private.old.key').decode()})

        r = requests.post(args.endpoint, json=data)

        if r.status_code == 200:
            print('Key successfully updated.')
        else:
            print('Key NOT updated.')
            print(r.text)

