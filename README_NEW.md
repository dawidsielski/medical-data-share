# Summary
[//]: # "Explain that the app has client and server side. 
Common prerequisites  / setup. Describe port changing to 8080 (FLASK_DEBUG) 
Make a note about docker with a link to detailed description"

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

By default it will run on port 80.

If you run into issue with running the app please run it with `sudo`.

#### Developer mode
If you want to run it using developer mode please run it using:
```
python3 app.py --dev
```
By default it will fin on port 80. You can change that by running e.g.:
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


# Server side
[\\]: # "Setup (if cannot be covered with the common setup in 1)
Starting the app
What can I do and how. (Adding users - generating keys)
Details of conf - adding data!"
    
# Client side
[\\]: # "
Setup (if cannot be covered with the common setup in 1)
What can I do and how"

# Linking nodes into a federation

## Start with a pair of nodes

## Adding more to existing federation
