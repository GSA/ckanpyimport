[![CircleCI](https://circleci.com/gh/GSA/ckanpyimport.svg?style=svg)](https://circleci.com/gh/GSA/ckanpyimport)

# ckanpyimport

Imports datasets from a data.json file into a CKAN instance. Data.gov uses this to move
datasets into Inventory.

## Usage

Edit `server.ini` with your information. Then run the import.

    $ python import.py <server-config-identifier> <org-name>

E.g.

    $ python import.py inventory va-gov


### Configuration

#### main

This section contains general configuration options, including the URL for the
data.json to import.


##### query

The URL location to the data.json file to import.


##### log_level

How verbose to log messages (default: INFO).


#### Server configuration

Each section can use a custom name to define multiple CKAN servers to import to.

##### url

The URL to the root CKAN server. e.g. https://inventory.data.gov

##### api

The API key to access the CKAN write API.


#### Example config

```
[main]
query = https://example.com/data.json

[inventory]
url = https://inventory.data.gov
api = <CKAN-API-key>
```


## Development


### Requirements

- [pipenv](https://pipenv.readthedocs.io/en/latest/)
- [pyenv](https://github.com/pyenv/pyenv) or [Python](https://python.org/) 2


### Setup

Install the dependencies.

    $ pipenv install --dev

Lint your code.

    $ make lint

Run the tests.

    $ make test


## Troubleshooting

### SSL certificate verify failed

    Error: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:726)>

Sometimes we're working with custom SSL Certificate Authorities, like in our
staging environment. Specify the CA certificate bundle that contains your CA. On
our staging instances, the system CA bundle should be sufficient:

    $ SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt python import.py inventory-staging va-gov
