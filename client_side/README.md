# Client side for medical-data-share

This folder contains python script which is responsible for getting data from medical-data-share website.

## Getting Started

Before running the app there are you have to properly set up folder structure.

First you have to have private key of the machine you will be asking in the `keys` folder

### Prerequisites

In order to run this application you have to have `python3` installed together with `python3-pip`.

### Installing

In order to run this script you will have to install some packages by running:
```
pip3 install pycrypto
```

### Running

Before you start you have to generate your own public and private keys by running

```buildoutcfg
python3 medical_data_share.py -g
```
or
```buildoutcfg
python3 medical_data_share.py --generate
```
This will generate public and private key together with user id.

Once you have done it in folder `keys/` there will be thee files. These are:
* `private.key`
* `public.<your-user-id>.key`
* `user_id` - holds only your user_id

At this point you will have to ask an administrator to add you to the server.

Once this is done you are able to make private requests to server.

If you are not added to the server you are only allowed to perform public operations.

### Getting the data

Once you are set up you can run this script with several options.

To successfully perform request you also have to specify:
* `-e` or `--endpoint` address of the variants endpoint (depending on a endpoint the request will be public or private)
* `-ch` or `--chrom` specifies number of chromosome
* `--start` starting position in chromosome
* `--end` ending position in chromosome
* `-q` or `--guery` simple query option for public requests
* `-r` or `--raw` will display raw response from the server
* `-a` or `--all-nodes` this will ask all available nodes for data

By default program will display decrypted result of the query.

If you want to save the output please add `-s` or `--save` option.

#### Query option

Query option is used only in public request.

Examples:
```
python3 medical_data_share.py -e http://0.0.0.0:8080/variants -q "21 9825797"
```
or
```
python3 medical_data_share.py -e http://0.0.0.0:8080/variants -q "21:9825797"
```

There are two formats available for query:
* `CHR:start[:stop]` - colon as seperator
* `CHR start[ stop]` - space as separator

## Important note
Public assess is restricted only for variants in a specific place. 

For private access you will have to have private key of the machine in order to sign the message.

### Examples:
For public request:
```
python3 medical_data_share.py -e http://localhost:8080/variants -s --chr 21 --start 9825797
```
For private request:

```
python3 medical_data_share.py -e http://localhost:8080/variants-private -s --chr 21
```

For both previous examples you can specify `-a` or `--all-nodes` option to aggregate variants information from all nodes.