from gensim import corpora, models, similarities
from gensim.parsing.preprocessing import STOPWORDS
from six import iteritems
from gensim.models.phrases import Phrases, Phraser
import pandas as pd
from utilities.analytics_utils import word_type, score_topics_lda, stream, streamer, corpus_sector_indices
import numpy as np
import os
import time
import psutil
import copy
import logging

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO  # ipython sometimes messes up the logging setup; restore

from config import NO_TOPICS, NO_SIM_TOPICS, THRESHOLD, TFIDF_THRESHOLD
from config import COMPLAINTS_WORD_TFIDF, CORPUS_METADATA, SIMILARITY_INDEX, TOPIC_LOOKUP, TOPIC_TIMESERIES

CORP_LOC = "./corpus_objects"


def reset_datafile(filename, columns):
    """Initialize an empty datafile with the appropriate column names"""
    with open(filename, "w") as f:
        f.write(",".join(columns)+"\n")

        
def print_memory():
    """Show the amount of memory currently occupied by the running Python script"""
    pid = os.getpid()
    py = psutil.Process(pid)
    memoryUse = py.memory_info()[0]/2.**30
    print('memory use: {0:2f}GB'.format(memoryUse))

    
def print_timing(func):
    """Wrapper to print out the time taken and memory occupied after function call"""
    def wrapper(*arg):
        print(str(func.__name__))
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print('%0.3fs' % ((t2-t1)))
        print_memory()
        return res
    return wrapper

    
@print_timing
def phrase_stream():
    """Create the bigram and trigram phraser objects from document streams"""
    phrases = Phrases(streamer(), delimiter= b" ")
    bigram = Phraser(phrases)
    del phrases
    triples = Phrases(bigram[streamer()], delimiter= b" ")
    trigram = Phraser(triples)
    return bigram, trigram
   
    
@print_timing    
def create_corpus():
    """Go through preprocessing steps to create and serialize mm format corpus"""
    bigram, trigram = phrase_stream()
    dictionary = corpora.Dictionary(trigram[bigram[streamer()]])

    #get the ids of words appearing only once or 0 times in corpus, and of stopwords
    unique_word_ids = [word_id for word_id, word_freq_cor in iteritems(dictionary.dfs) if word_freq_cor <= 1]
    gensim_stopwords_ids = [dictionary.token2id[stopword] for stopword in STOPWORDS if stopword in dictionary.token2id]
    
    #remove the words appearing only once or 0 times in corpus, and stopwords, compactify dictionary
    dictionary.filter_tokens(unique_word_ids + gensim_stopwords_ids)
    dictionary.compactify()
    
    # Save and load the dict
    dictionary.save(os.path.join(CORP_LOC, 'OmbudsDictionary.dict'))
    dict_loaded = corpora.Dictionary.load(os.path.join(CORP_LOC, 'OmbudsDictionary.dict'))
    
    corpora.MmCorpus.serialize(os.path.join(CORP_LOC, 'OmbudCorpus.mm'), (dict_loaded.doc2bow(x) for x in trigram[bigram[streamer()]]))
    corpus_loaded = corpora.MmCorpus(os.path.join(CORP_LOC, 'OmbudCorpus.mm'))

    return corpus_loaded, dict_loaded


@print_timing   
def create_tfidf(corpus_loaded):
    """Convert corpus into TFIDF format"""
    tfidf = models.TfidfModel(corpus_loaded)
    return tfidf[corpus_loaded]


@print_timing
def create_tfidf_frame(corpus_loaded, dict_loaded):
    """Create an output file for loading into SAS VA (Wordcloud View)"""
    cor_frames = []
    for ind, text in enumerate(tfidf_corpus):
        # Create list of word, tfidf weighting pairs
        word_tfidf = [[dict_loaded[word[0]], word[1]] for word in text if word[1] > TFIDF_THRESHOLD] 
        unzipped_wordfreqs = list(zip(*word_tfidf))
        if len(unzipped_wordfreqs) == 0:
            word = ['None']
            word_freq = [0]
        else:
            word = unzipped_wordfreqs[0]
            word_freq = unzipped_wordfreqs[1]
        cor_frames.append(pd.DataFrame({'doc_id': ind, 'Word': word, 'Freq': word_freq}))
    
    combined_frame = pd.concat(cor_frames)
    combined_frame['Word Type'] = combined_frame['Word'].apply(word_type)
    combined_frame.to_csv(COMPLAINTS_WORD_TFIDF, index=False)

    
@print_timing
def create_metadata():
    """
    Create metadata frame for joining on indices in SAS VA
    returns dictionary for corpus - sector lookup
    """
    #Exctract and output the metadata
    meta_data_dictionary=[]
    for row in stream():
        del row['Text']
        try:
            del row["raw_text"]
        except:
            pass
        meta_data_dictionary.append(row)
        
    meta_frame = pd.DataFrame(meta_data_dictionary)
    del meta_data_dictionary
    try:
        del meta_frame['null']
    except:
        pass
    meta_frame.to_csv(CORPUS_METADATA)
    # Create integer sector lookup
    unique_sectors = list(meta_frame["IndustrySector"].unique())
    sector_reference = dict(zip(unique_sectors, range(len(unique_sectors))))
    return meta_frame["IndustrySector"].apply(lambda x: sector_reference[x]).to_dict(), sector_reference

 
@print_timing
def create_similarities(tfidf_sector_corpus, index_alignment):
    """Creates similarity index dataset for SAS VA dashboard (Document similarities)"""
    simi_mod = models.LsiModel(tfidf_sector_corpus, id2word=dict_loaded, num_topics=NO_SIM_TOPICS)
    sim_corpus = simi_mod[tfidf_sector_corpus]
    lookup_func = np.vectorize(index_alignment.get)
    #Constructing the similarity matrix, exporting similarity table
    doc_index = similarities.MatrixSimilarity(sim_corpus)
    themed_sim_matrix = np.hstack((np.array([
                                             lookup_func([n]*x[x > THRESHOLD].shape[0]),
                                             lookup_func(np.where(x > THRESHOLD)[0]), 
                                             x[x > THRESHOLD]]) 
                                             for n, x in enumerate(doc_index[sim_corpus])
                                             if x[x > THRESHOLD].shape[0] > 0))

    with open(SIMILARITY_INDEX, 'ab') as f:
        np.savetxt(f, themed_sim_matrix.transpose(), delimiter=",", fmt='%i,%i,%1.4f')

        
@print_timing
def track_topics(sector_corpus, index_lookup, cor_dict):
    lsi_mod=models.LdaModel(sector_corpus, id2word=cor_dict, num_topics=NO_TOPICS, passes=25)
    
    topics_table = pd.DataFrame([{**{"doc_id":indices[n]}, **score_topics_lda(lsi_mod, x, sect_ind)} for n, x in enumerate(sector_corpus)])
    topics_table.to_csv(TOPIC_TIMESERIES, mode='a', header=False, index=False)
    del topics_table
    
    # Export topics lookup
    transformed_topics = [(x[0], ", ".join([str(y[0]) for y in x[1][:7]])) for x in lsi_mod.show_topics(num_topics=NO_TOPICS, formatted=False)]
    theme_lookups=pd.DataFrame([{"Topic": "Topic"+str(x[0])+sect_ind, "Vector": x[1]} for x in transformed_topics])
    theme_lookups.to_csv(TOPIC_LOOKUP, mode='a', header=False, index=False)
    del theme_lookups
        
if __name__ == '__main__':
    timestart = time.time()
    corpus_loaded, dict_loaded = create_corpus()
    tfidf_corpus = create_tfidf(corpus_loaded)
    create_tfidf_frame(corpus_loaded, dict_loaded)
    sectors_dict, sector_reference = create_metadata()
    filtered_dict = copy.deepcopy(dict_loaded)
    filtered_dict.filter_extremes()
    old2new = {dict_loaded.token2id[token]:new_id for new_id, token in filtered_dict.items()}
    vt = models.VocabTransform(old2new)
    print("Length of overall corpus is: "+str(len(corpus_loaded))+" docs")
    
    # Initialize the empty csvs to append to
    reset_datafile(SIMILARITY_INDEX, ["doc_id", "Similar", "Scores"])
    reset_datafile(TOPIC_TIMESERIES, ["Unused"]*NO_TOPICS+["doc_id", "top_topic1", "top_topic2", "top_topic3"])
    reset_datafile(TOPIC_LOOKUP, ["Topic", "Vector"])
    
    for sect_ind, sector in sector_reference.items():
        print("Sector is: "+sect_ind)
        indices = corpus_sector_indices(sector, sectors_dict)
        # Lookup of sector specific indices vs overall corpus
        ref_lookup = dict(zip(range(len(indices)), indices))
        
        # Create serialized sector specific corpus
        corpora.MmCorpus.serialize(os.path.join(CORP_LOC, 'sector_corpus.mm'), corpus_loaded[indices])
        sector_corpus = corpora.MmCorpus(os.path.join(CORP_LOC, 'sector_corpus.mm'))
        
        tfidf_sector_corpus = create_tfidf(sector_corpus)
        
        # Output similarity and topic tables
        create_similarities(tfidf_sector_corpus, ref_lookup)
        track_topics(vt[sector_corpus], ref_lookup, filtered_dict)
        
    
    print("Small corpus time taken:", time.time() - timestart)