from scraper.pdf_clean_utils import create_corpus
import requests
import os
import json
from cloudant.query import Query
# Enable the required Python libraries for working with Cloudant NoSQL DB.

from config import connect_to_client, PROXIES, FILE_NAME, DB_NAME


def get_retrieved_complaints():
    client = connect_to_client()
    retrieved_complaints = [int(x["id"]) for x in client[DB_NAME].all_docs()['rows']]
    if len(retrieved_complaints) == 0:
        retrieved_complaints = [100000]
    return retrieved_complaints


def scrape_ahead_n_complaints(n_ahead=1000):
    """
    :param n_ahead:
    :return:
    """
    already_scraped = get_retrieved_complaints()
    start_no = max(already_scraped)
    update_corpus(start_no, already_scraped, n_ahead)


def update_corpus(latest_number, retrieved_complaints, n_ahead):

    client = connect_to_client()
    database = client[DB_NAME]

    for n in range(latest_number + 1, latest_number + n_ahead):
        url = "http://www.ombudsman-decisions.org.uk/viewPDF.aspx?FileID="+str(n)
        print(url)
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
                corpus_entry['_id'] = str(n)
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

