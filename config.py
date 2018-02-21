FILE_NAME = "./scraper/scraping_data/small_corpus2.json"

COMPANY_ALIASES = "natwest halifax amex bos rb uki lv rsa urv wonga quick quid pound pocket"
NO_TOPICS = 15
NO_SIM_TOPICS = 200
THRESHOLD = 0.70
TFIDF_THRESHOLD = 0.027

# Output file locations
COMPLAINTS_WORD_TFIDF = "./output_data/complaints_tfidf.csv"
CORPUS_METADATA = "./output_data/corpus_metadata.csv"
SIMILARITY_INDEX = "./output_data/sim_index.csv"
TOPIC_LOOKUP = "./output_data/topic_lookup.csv"
TOPIC_TIMESERIES = "./output_data/topic_timeseries.csv"