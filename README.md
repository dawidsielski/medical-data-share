# DataShare

DataShare is an online tool for sharing medical variants information.

## Getting Started

Before running the app there are you have to perform some setup.

First clone the repo by running `git clone`.
Then in the folder you will see file called `config.ini`. 
Depending on your laboratory you will have to fill in the variables inside.

Variables you will have to set are:
* LABORATORY_NAME - this name will be displayed on a website
* NODE_ADDRESS - this is an address for this node
* TIMEZONE - this is a timezone variable
* MAX_PUBLIC_VARIANT_REQUEST_LIMIT - this holds daily limit for public requests

### Prerequisites

In order to run this application you have to have `python3` installed together with `python3-pip`.

### Installing

In order to run this app you have to install `requirements.txt` file by running:
```
pip3 install -r requirements.txt
```

### Running

When everything is installed you have to change directory to `medical-data-share`. Then just run `python3 app.py`.

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

Special thanks to my supervisor Pawel Sztromwasser.