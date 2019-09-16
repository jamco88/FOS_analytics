import getpass
import sys
import os
import json
from cloudant.client import Cloudant

FILE_NAME = "./scraper/scraping_data/small_corpus2.json"

def create_proxies():
    """Generate the global proxies required to access web through LBG network"""
    username = getpass.getuser()
    password = getpass.getpass()
    return {'http': 'http://' + username + ':'+password+'@PROXYARRAY.SERVICE.GROUP:8080/',
            'https': 'https://'+username+':'+password+'@PROXYARRAY.SERVICE.GROUP:8080/'}


if sys.platform == 'win32':
    print("proxy password:")
    PROXIES = create_proxies()
    os.environ["HTTP_PROXY"] = PROXIES["http"]
    os.environ["HTTPS_PROXY"] = PROXIES["https"]
else:
    PROXIES = {}


COMPANY_ALIASES = "natwest halifax amex bos rb uki lv rsa urv wonga quick quid pound pocket barclaycard ipa"
NO_TOPICS = 15
NO_SIM_TOPICS = 200
THRESHOLD = 0.75
TFIDF_THRESHOLD = 0.027

# Output file locations
COMPLAINTS_WORD_TFIDF = "./output_data/complaints_tfidf.csv"
CORPUS_METADATA = "./output_data/corpus_metadata.csv"
SIMILARITY_INDEX = "./output_data/sim_index.csv"
TOPIC_LOOKUP = "./output_data/topic_lookup.csv"
TOPIC_TIMESERIES = "./output_data/topic_timeseries.csv"

DB_NAME = "fos_decisions"


def connect_to_client():
    if 'VCAP_SERVICES' in os.environ:
        # Yes we are, so get the service information.
        vcap_servicesData = json.loads(os.environ['VCAP_SERVICES'])
        #print(vcap_servicesData)
        # Look for the Cloudant NoSQL DB service instance.
        cloudantNoSQLDBData = vcap_servicesData['cloudantNoSQLDB Dedicated']
        # Log the fact that we successfully found some Cloudant NoSQL DB service information.
        print("Got cloudantNoSQLDBData\n")
        # Get a list containing the Cloudant NoSQL DB connection information.
        credentials = cloudantNoSQLDBData[0]

        # Get the essential values for our application to talk to the service.
        credentials_data = credentials['credentials']

    else:
        # Delete these credentials from
        with open("cloudant_credentials.json", "r") as creds_file:
            credentials_data = json.load(creds_file)

    username = credentials_data['username']
    password = credentials_data['password']
    service_url = credentials_data['url']

    # We now have all the details we need to work with the Cloudant NoSQL DB service instance.
    # Connect to the service instance.
    client = Cloudant(username, password, url=service_url)
    client.connect()
    return client

