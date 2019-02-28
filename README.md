# DataShare

DataShare is an online tool for sharing medical variants information.

This application gives two interfaces. One is public in which there is a limited amount of requests per day.
The private one which gives several options for variants data request.

## Getting Started

Before running the app there are you have to perform some setup.

First clone the repo by running
 ```
 git clone https://github.com/dawidsielski/medical-data-share.git
 ```
Then in the folder you will see file called `config.ini`. 
Depending on your laboratory you will have to fill in the variables inside.

Variables you will have to set are:
* LABORATORY_NAME - this name will be displayed on a website
* NODE_ADDRESS - this is an address for this node
* TIMEZONE - this is a timezone variable
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

### Adding to existing federation

#### For the user of the new Node:
1. Using medical_data_share.py client (can be found in client_side folder) generate your own key pair by running:
   ```
   python3 medical_data_share.py -g
   ```
   This will ask you for the name of the node. Please provide the same laboratory name as in `config.ini` file. Then hit enter.

   Now in keys folder you have three files.

2. From keys folder copy the file names `public.<your_username>@<your_node_name>.key` to the folder called `public_keys` of the server that you are running the app.

3. On the server there will be folder called keys. Please copy file called `public.key` to your computer.

4. Now you must ask an authorized person to add your node to federation. To have that please send to this person the following information:
    * laboratory_name (the same as in config file)
    * laboratory_address (the same as in config file)
    * `public.key` file downloaded from a server

5. Now run:
   ```
   python3 medical_data_share.py -e http://<laboratory_from_federation_address>/nodes -s
   ```

   This will generate a folder called `nodes`. Please copy the contents of this folder to the remote `nodes` folder on your server.


#### For the user that is asked to add node:
1. When you recieve a message with the data including:
   * laboratory_name (the same as in config file)
   * laboratory_address (the same as in config file)
   * `public.key` file downloaded from a server
   
   you can run the following command:
   ```
   python medical-data.share.py -e http://<your_laboratory_address>/add-node --lab-name <laboratory_name_provided> --lab-address <laboratory_address provided> -k <path_to_a_public_key_provided>
   ```
   Running this will add new node to every node in federation.

### How to supply data

#### Tabix files
The application supports two genome types. First is hg19 and the second is hg38.

By default application works with hg19 files provided but there is a possibility for supplying files for hg38.

The folder structure must look like this provided below. 

```
data
├── hg19
│   ├── gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz
│   └── gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz.tbi
└── hg38
    ├── gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz
    └── gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz.tbi
```

The filenames of the hg19 or hg38 tabix filenames must be set in config file under DATA section.

#### Other support
In progress.

### Key check (private)

The application requires from you updating keys by the number of days specified in the config file.

If at some point you will not be able to perform private queries please check if your key needs to be updated.

This can me done bu running:
```
python medical_data_share.py -e http://<your_laboratory_address>/ -ck
```
Running this will tell you if your key needs an update or not.



### Dockerfile

If you want to use docker there is a Dockerfile provided.

To build the image it you have to run:
```
docker build --tag datashare .
```

Starting container:
```
docker run --name medical-data-share -p 80:80 -d datashare
```

## Authors

* **Dawid Sielski** - *Initial work* - [Dawid Sielski](https://github.com/dawidsielski)

## License

TODO

## Acknowledgments

Special thanks to my supervisor [Paweł Sztromwasser](https://github.com/seru71)