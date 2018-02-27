# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 10:06:17 2017

@author: 9848504
"""

from pdf_clean_utils import create_corpus
from gensim.summarization import summarize
import requests
from getpass import getpass, getuser
import os
import json

FILE_NAME = "./scraping_data/small_corpus2.json"

def get_existing_complaints():
    visited_urls = []
    with open(FILE_NAME, "r", encoding="ISO-8859-1") as f:
        for line in f.readlines():
            visited_urls.append(json.loads(line)["FileID"])
    return visited_urls

def update_corpus():
    password = getpass()
    username = getuser()
    proxies = {'http': 'http://' + username + ':'+password+'@PROXYARRAY.SERVICE.GROUP:8080/', 'https': 'https://'+username+':'+password+'@PROXYARRAY.SERVICE.GROUP:8080/'}
      
    #start_no = 163401
    start_no = 125416
    
    # Check for the existence of the OmbudsmanCorpus file
    if os.path.isfile(FILE_NAME):
        retrieved_complaints = get_existing_complaints()
    else:
        print("No file")
        retrieved_complaints = []
    
    for n in range(start_no, start_no-30000, -1):
        url = "http://www.ombudsman-decisions.org.uk/viewPDF.aspx?FileID="+str(n)
        #print(url)
        n_trys = 3
        if n not in retrieved_complaints:
            for attempt_no in range(n_trys):
                try:
                    x = requests.get(url, proxies=proxies)
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
