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

The available options are:
* `--public` this will perform request for publicly available data
* `--private` this will perform request for private available data

To successfully perform request you also have to specify:
* `-e` or `--endpoint` address of the variants endoint
* `-ch` or `--chrom` specifies number of chromosome
* `--start` starting position in chromosome
* `--end` ending position in chromosome

By default program will display information gathered.

If you want to save the output please add `-s` or `--save` option.

## Important note
Public assess is restricted only for variants in a specific place. 

For private access you will have to have private key of the machine in order to sign the message.

### Examples:
```buildoutcfg
python3 medical_data_share.py --public -e http://localhost:8080/variants -s --chr 21 --start 9825797
```

```buildoutcfg
python3 medical_data_share.py --private -e http://localhost:8080/variants-private -s --chr 21
```