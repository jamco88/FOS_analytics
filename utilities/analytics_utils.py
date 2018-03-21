import pandas as pd
from heapq import nlargest
import csv
import ast
import json

from config import FILE_NAME, COMPANY_ALIASES, NO_TOPICS


class OmbudsmanLibrary(object):
    def __iter__(self):
        with open(FILE_NAME, "r", encoding="ISO-8859-1") as jsonfile:
            for i, row in enumerate(jsonfile.readlines()):
                if i > 0:
                    yield json.loads(row)

def word_type(x):
    if len(x.split()) == 1:
        return "Word"
    elif len(x.split()) == 2:
        return "Bigram"
    else:
        return "Phrase"
                          
def score_topics(lsi_model, tfidf_corpus, topic, select_topics = 3):
    theme_outputs = lsi_model[tfidf_corpus]
    topics = ["Topic"+str(x[0])+topic for x in theme_outputs]
    scores = [x[1] for x in theme_outputs]
    abs_scores = [abs(x) for x in scores]
    topic_series = dict(zip(topics,abs_scores))
    main_topics = ["Topic"+str(abs_scores.index(top_score))+topic for top_score in nlargest(select_topics, abs_scores)]
    top_top_titles = ["top_topic" + str(n) for n in range(1, select_topics+1)]
    topic_info_dict = {**topic_series, **dict(zip(top_top_titles, main_topics))}
    return topic_info_dict

    
def score_topics_lda(lda_model, corpus, sector, select_topics = 3):
    theme_outputs = lda_model[corpus]
    topic_names = {x:"Topic"+str(x)+sector for x in range(NO_TOPICS)}
    sorted_topics = sorted([x for x in theme_outputs], key=lambda x: x[1], reverse=True)
    top_top_titles = ["top_topic" + str(n) for n in range(1, select_topics+1)]
    topic_series = dict(map(lambda x: (topic_names[x[0]], x[1]), sorted_topics))
    main_topics = list(map(lambda x: (topic_names[x[0]]), sorted_topics))[:3]
    topic_info_dict = {**topic_series, **dict(zip(top_top_titles, main_topics))}
    return topic_info_dict
                  
def streamer():
    return map(lambda x: x["Text"], stream())
    
def stream():
    mem_friend_corpus = OmbudsmanLibrary()
    for row in mem_friend_corpus:
        row['Text'] = [word for word in row['Text'] if (word not in row['Business'].lower() + COMPANY_ALIASES)]
        row['summary'] = row['summary'].replace("\n", ". ").replace("\r", ". ")[8:]
        yield row



def corpus_sector_indices(sector, sectors_dict):
    return [k for k,v in sectors_dict.items() if v == sector]
            
class Raw_CSV(object):
     def __iter__(self):
        with open(FILE_NAME, "r", encoding = "ISO-8859-1") as csvfile:
            datareader = csv.reader(csvfile)
            for row in datareader:
                yield row
                
                
def fix_csv(filename = FILE_NAME, output="cleaned_large.csv"):
    """This function cleans out the rows which have malformed csv bits"""
    for i, row in enumerate(Raw_CSV()):
        if i == 0:
            with open(output, 'a') as f:
                pd.DataFrame(row).T.to_csv(f, header=False, index=False)
                f.close()
        else:
            # Check parameters to ensure 
            if row[0].isdigit() and row[15][0:4] == 'www.':
                with open(output, 'a', encoding='utf-8') as f:
                    pd.DataFrame(row).T.to_csv(f, header=False, index=False, encoding='utf-8')
            else:
                print("BAD ROW", i)
                


def make_json():
    csvfile = open('cleaned_large.csv', 'r', encoding='ISO-8859-1')
    jsonfile = open('large_json.json', 'w')
    
    fieldnames = ("Index", "Author",	"Business",	"CreationDate",	"Creator",	"DecisionDate",	"Description",	"Identifier",	"IndustrySector",	"ModDate",	"Outcome",	"Producer",	"Subject",	"Title",	"Text",	"URL",	"FileID")
    reader = csv.DictReader( csvfile, fieldnames)
    for i, row in enumerate(reader):
        print(row["Text"])
        if i > 0:
            row["Text"] = ast.literal_eval(row["Text"])
            json.dump(row, jsonfile)
            jsonfile.write('\n')