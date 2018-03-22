from getpass import getpass, getuser
import sys

FILE_NAME = "./scraper/scraping_data/small_corpus2.json"

if sys.platform == "win32":
    print("Get password")
    password = getpass()
    username = getuser()
    PROXIES = {'http': 'http://' + username + ':' + password + '@PROXYARRAY.SERVICE.GROUP:8080/',
               'https': 'https://' + username + ':' + password + '@PROXYARRAY.SERVICE.GROUP:8080/'}
else:
    PROXIES = {}


COMPANY_ALIASES = "natwest halifax amex bos rb uki lv rsa urv wonga quick quid pound pocket barclaycard ipa"
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