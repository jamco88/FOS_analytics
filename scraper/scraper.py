from scraper.pdf_clean_utils import create_corpus
import requests
import os
import json
from cloudant.query import Query
# Enable the required Python libraries for working with Cloudant NoSQL DB.
from cloudant.client import Cloudant
from config import PROXIES, FILE_NAME, DB_NAME


def get_retrieved_complaints():
    client = connect_to_client()
    retrieved_complaints = [x["FileID"] for x in Query(DB_NAME, selector={"_id": {"$gt": 0}}, fields=["FileID"], sort=[{"FileID": "asc"}]).result]
    client.disconnect()
    print("EXISTING", retrieved_complaints)
    return retrieved_complaints


def existing_complaints():
    with open(FILE_NAME, "r", encoding="ISO-8859-1") as f:
        for line in f.readlines():
            yield json.loads(line)["FileID"]


def scrape_ahead_n_complaints(n_ahead=1000):
    """

    :param n_ahead:
    :return:
    """
    already_scraped = get_retrieved_complaints()
    start_no = max(already_scraped) + n_ahead
    update_corpus(start_no, already_scraped)

def update_corpus(latest_number, retrieved_complaints):

    #start_no = 171183 - 169414 - 162415 - 132416 - 95416
    client = connect_to_client()
    database = client[DB_NAME]

    for n in range(latest_number, max(retrieved_complaints), -1):
        url = "http://www.ombudsman-decisions.org.uk/viewPDF.aspx?FileID="+str(n)
        #print(url)
        n_trys = 3
        if n not in retrieved_complaints:
            for attempt_no in range(n_trys):
                try:
                    x = requests.get(url, proxies=PROXIES)
                    attempt_no = 0
                    break
                except:
                    print("Error retrieving ", url, "Attempt: ", attempt_no)
            # Break out if url failed
            if attempt_no == n_trys - 1:
                print("URL FAIL")
                continue
            print(x.status_code, x.url, x.headers['Content-Type'])
            if x.status_code == 200 and 'text/html' not in x.headers['Content-Type']:
                pdf_corpus, meta_data, raw_text = create_corpus(x)
                #print(meta_data)
                corpus_entry = meta_data.copy()
                corpus_entry['Text'] = pdf_corpus
                corpus_entry['URL'] = x.url[7::]
                corpus_entry['FileID'] = n
                corpus_entry['raw_text'] = raw_text
                corpus_entry['summary'] = raw_text.replace(".", ". ").replace("\n", ". ").replace("\r", ". ")[:400]+"..."

                new_doc = database.create_document(corpus_entry)

                # Check that the document exists in the database.
                if new_doc.exists():
                    print("Document '{0}' successfully created.".format(n))

                # with open(FILE_NAME, 'a', encoding='ISO-8859-1') as f:
                #     f.write(json.dumps(corpus_entry.to_dict()))
                #     f.write("\n")
    client.disconnect()


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
        print(credentials_data)


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

