from scraper.pdf_clean_utils import create_corpus
import requests
import os
import json
from config import PROXIES, FILE_NAME


def get_retrieved_complaints(filename=FILE_NAME):
    if os.path.isfile(filename):
        print("getting existing")
        retrieved_complaints = [num for num in existing_complaints()]
    else:
        print("No file")
        retrieved_complaints = [0]
    retrieved_complaints = [171181]
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

    retrieved_complaints = [171181]
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
            if attempt_no == n_trys -1:
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

                with open(FILE_NAME, 'a', encoding='ISO-8859-1') as f:
                    f.write(json.dumps(corpus_entry.to_dict()))
                    f.write("\n")
