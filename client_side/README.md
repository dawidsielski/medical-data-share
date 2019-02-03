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

The script runs feom command line by running `python3 medical_data_share.py`.

There exist several options available.

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