import requests
import argparse
import json


def prepare_public_request(chrom=None, start=None, end=None):
    data = {
        'chrom': chrom,
        'start': start,
        'end': end
    }
    return data


def data_request(endpoint, chrom=None, start=None, end=None):
    return requests.post(endpoint, json=prepare_public_request(chrom, start, end))


def handle_request(r, args):
    if r.status_code == 200:
        if args.verbose:
            print(r.text)

        if args.save:
            with open('data.json', 'w') as file:
                json.dump(json.loads(r.text), file)
            print('File has been saved.')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--public', action='store_true', default=False)
    group.add_argument('--private', action='store_true', default=False)

    parser.add_argument('-e', '--endpoint', required=True, help='Endpoint to which request is performed.')
    parser.add_argument('-ch', '--chrom', type=int, help='Chromosome number.')
    parser.add_argument('--start', type=int, help='Starting position.')
    parser.add_argument('--stop', type=int, help='Ending position.')
    parser.add_argument('-s', '--save', action='store_true', help=)
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()
    print(args)

    if args.public:
        if args.chrom and args.start:
            r = data_request(args.endpoint, args.chrom, args.start)
            handle_request(r, args)
    elif args.private:
        r = data_request(args.endpoint, args.chrom, args.start, args.stop)
        handle_request(r, args)


# python3 medical_data_share.py --public -e http://localhost:8080/variants
# python3 medical_data_share.py --public -e http://localhost:8080/variants -s
# python3 medical_data_share.py --public -e http://localhost:8080/variants -s --chr 21 --start 9825797

# python3 medical_data_share.py --private -e http://localhost:8080/variants-private -s --chr 21 --start 9825797 --stop 9825850
# python3 medical_data_share.py --private -e http://localhost:8080/variants-private -s --chr 21
