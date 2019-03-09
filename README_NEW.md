# Summary
[//]: # "Explain that the app has client and server side. 
Common prerequisites  / setup. Describe port changing to 8080 (FLASK_DEBUG) 
Make a note about docker with a link to detailed description"

DataShare is an online tool for sharing medical variants information.

The application consists of two modules:
* server_side
* client_side 

#### Server side
Server side contains FLASK web application which provides an interface for secure share of genetic variants information in two modes:
* private
* public

By default ones can perform public operation which will result in the information of genetic variants in specific place. **Public option is daily limited.**

To obtian access to private operations you have to be an authorized user of any of the lab in federation.

#### Client side
Client side contains simple python script which is responsible for making public and private queries together with checking user keys, updating user keys, adding new node to federation.


## Dockerfile
If you want to use docker there is a Dockerfile provided.

To build the image it you have to run:
```
docker build --tag datashare .
```

Starting container:
```
docker run --name medical_data_share -p 80:80 -d datashare
```


# Server side
[\\]: # "Setup (if cannot be covered with the common setup in 1)
Starting the app
What can I do and how. (Adding users - generating keys)
Details of conf - adding data!"

## Getting Started

First clone the repo by running
 ```
 git clone https://github.com/dawidsielski/medical-data-share.git
 ```
Then (after entering 'medical_data_share' folder) you will see file called `config.ini`. 
Depending on your laboratory you will have to fill in the variables inside.

Variables you will have to set are:
* LABORATORY_NAME - this name will be displayed on a website
* NODE_ADDRESS - this is an address for this node
* TIMEZONE - this is a timezone variable depending on your location
* MAX_PUBLIC_VARIANT_REQUEST_LIMIT - this holds daily limit for public requests

### Prerequisites

In order to run this application you have to have `python3` (version 3.6 is required) installed together with `python3-pip`.

### Installing

In order to run this app you have to install `requirements.txt` file by running:
```
pip3 install -r requirements.txt
```

### Running

Running the application is simple as running `python3 app.py` from commandline.

By default it will run on port 80 for which you will need root proviledges.

If you run into issue with running the app please try running it with `sudo`.

### Developer mode
If you want to run it using developer mode please run it using:
```
python3 app.py --dev
```
By default it will run on port 80. You can change that by running e.g.:
```
python3 app.py --dev -p 8080
```

### Adding data

By default the app provides support for hg19 tabixed files. You can also add hg38 file.

If you have these files ready please intert them presented as follows:
```
data
├── hg19
│   ├── gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz
│   └── gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz.tbi
└── hg38
    ├── tmp_hg38_sorted.tsv.gz
    └── tmp_hg38_sorted.tsv.gz.tbi
```

Once this is done please enter the filenames of tabixed file into `config.ini` under `DATA` section.
Example:
```
[DATA]
HG_19_FILENAME = gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz
HG_38_FILENAME = tmp_hg38_sorted.tsv.gz
```


# Client side
[\\]: # "
Setup (if cannot be covered with the common setup in 1)
What can I do and how"

## First run

By default there is only possibility to query public variants.

If you want to perform private operations you have to:
   1. Generate your own keys and username by running:
	```
	python3 medical_data_share.py -g
	```
	You will be prompted to specify your node laboratory name (the same as in config file of the node).
	Your username will be generated automatically.
   2. Copy your public key from `keys` folder (public.<your_username>@<your_node>.key) to `public_user_keys` of the node of your lab.
   3. Now you are ready to perform private queries.

**NOTE:
Every key pair has its own expiration time which is set by config file (section 'NODE' variable 'USER_KEY_EXPIRATION_TIME' by default set to 30 days)**

#### Check user key

To check user key please run:
```
python medical_data_share.py -e <your_laboratory_address>/ -ck
# or
python medical_data_share.py -e <your_laboratory_address>/ --check-key
```

As an output you will be told if you have o update your keys or not.

#### Updating user keys

To update personal user keys please run:
```
python medical_data_share.py -e <your_laboratory_address>/ -uk
# or
python medical_data_share.py -e <your_laboratory_address>/ --update-user-key
```

## Available nodes

If you want to display available nodes please run:
```
python3 medical_data_share.py -e <laboratory_from_federation_address>/nodes -v
```

If you want to save available nodes please run:
```
python3 medical_data_share.py -e <laboratory_from_federation_address>/nodes -s
```
This will generate `nodes` folder in which information ablut the nodes will be saved.

This will generate a folder called nodes. 

| Command                                                                                | Description                                         | Endpoint        | Type      | Supported |
|----------------------------------------------------------------------------------------|-----------------------------------------------------|-----------------|-----------|-----------|
| python3 medical_data_share.py --priv -ch 1 --start 1 --stop 10                         | Query from start to end                             | From config     | prywatne  | No        |
| python3 medical_data_share.py -e <endpoint>/variants-private -ch 1 --start 1 --stop 10 | Query from start to end                             | Custom endpoint | prywatne  | Yes       |
| python3 medical_data_share.py --priv -ch 1 --start 1                                   | Query specified posiion                             | From config     | prywatne  | No        |
| python3 medical_data_share.py -e <endpoint>/variants-private -ch 1 --start 1           | Query specified posiion                             | Custom endpoint | prywatne  | Yes       |
| python3 medical_data_share.py -ch 1 --start 1                                          | Query specified posiion                             | From config     | publiczne | No        |
| python3 medical_data_share.py -ch 1 --start 1 --end 10                                 | Query specified posiion (will omit end information) | From config     | publiczne | No        |
| python3 medical_data_share.py -e <endpoint>/variants -ch 1 --start 1                   | Query specified posiion                             | Custom endpoint | publiczne | Yes       |
| python3 medical_data_share.py -e <endpoint>/variants -ch 1 --start 1 --end 10          | Query specified posiion (will omit end information) | Custom endpoint | publiczne | Yes       |

Sample endpoint: `http://0.0.0.0:8080

Every command is supported with `-gb hg38` option for hg38 coordinates.
If you want to merge results from all nodes please specify `-a` or `--all` option.

# Linking nodes into a federation

## For the node that will be added (NODE)
   1. Run the application for the first time.
   2. Copy public.key file from keys folder on the server.
   3. Send this file to the FEDERATION node together with information about node address, node name.
   4. Using medical_data_share.py from client_side perform `python3 medical_data_share.py -n -e FEDERATION`
   5. Copy nodes folder from client_side to nodes folder on the server.
	
## For the node in federation (FEDERATION)

   1. If you are an authorized user in the node in FEDERATION please run:
   ```
   python3 medical_data_share.py -e <endpoint>/add-node --key <path_to_public_key_file> --lab-name <lab_name> --lab-address <lab_address>
   ```
   Running this will add new node for every node in the FEDERATION.
