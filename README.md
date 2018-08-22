# Finincial Ombudsman Service Complaints Analytics
Data analysis developed by Risk Innovation team to discover trends in Financial Ombudsman Complaints data to give better legal oversite of emerging threats.

The application runs in Cloud Foundry on the LBG sandbox - currently in the DEV environment ([FOS tracker](https://fos-analytics.lbg.eu-gb.mybluemix.net/))<hr></hr>

The flat files produced are then surfaced in an interactive SAS Visual Analytics report which allows users to explore to corpus in a number of different ways, with the overlay of text analytics.

## <a name="team-members"></a>Table of Contents
* [Team Members](#team-members)
* [Background](#background)
* [Getting Started](#get-started)
* [Theory](#theory)
* [Contribute](#contribute)

## <a name="team-members"></a>Team Members
#### Development
* **(Deprecated)** "Sven Harris" <sven.harris@lloydsbanking.com>
* "Jack Grimes" <jack.grimes@lloydsbanking.com>
* "Gordon Baggott" <gordon.baggott@lloydsbanking.com>

#### Business Stakeholders
* "Tricia McGrath" <patricia.mcgrath@lloydsbanking.co.uk> - Legal Developments, Group Legal
* "Jacqueline Lawrence" <Jacqueline.JB.Lawrence@lloydsbanking.com> - Legal Developments, Group Legal

## <a name="background"></a>Background
Teams in Group Legal are required to understand the external legal and regulatory environments and spot trends or patterns that may come to materially impact the group (e.g. PPI). The Financial Ombudsman Service publishes complaints on which it makes decisions whether or not to uphold, and the remediatory required to be taken by the company involved. This is a rich source of information about consumer trends, and potential compliance risks, however the volumes of complaints mean it is unfeasible to capture and understand all of this information by reading all of the complaint releases (the corpus contains over 100,000 documents).

This motivated the development of an application with which the high level trends can be abstracted, still with the capabilty to drill down and aggregate by different filters as well as access the original complaint documents.

## <a name="get-started"></a>Running the Process

### Scraping and table production
The web application is scheduled to scrape the latest complaints from the FOS website and produce the output tables, these can be downloaded from https://fos-analytics.lbg.eu-gb.mybluemix.net/.

| Activity | Schedule |
| ------------- | ------------- |
| Scraping 1500 complaints ahead | monday, wednesday - friday |
| Table creation | tuesday, saturday |

**Note: Scheduled runs don't always execute successfully, on restarting the application the analytics tables will run, this can take around 8 hours if you're unlucky, which you are, I'm sorry. Also if you notice the latest complaint hasn't go any bigger check on the website and make sure they haven't skipped ahead more than 1500 so you might want to do something about that.**


### Updating the report
Each of the tables produced by the Python text analytics needs to be loaded into SAS, queries then need to be run to produce the full tables for the reports. Finally some of the default values should be updated in the report so that everything looks fresh.

##### Loading the tables
The below tables need to be loaded into SAS VA, this can be done in SAS Visual Data Builder (to import File > Import Data...). They need to be uploaded into the following location **Shared Data/SAS Visual Analytics/Public/LASR/FOS scanning/RAW2** 

All tables need to be uploaded with the suffix of **_tng** - This was due to permission errors.

**Note: When uploading the TOPIC_TIMESERIES table set rows to scan to 100,000 otherwise some values can become truncated**

| Python Name   | SAS Name      | Description  |
| ------------- | ------------- |---------------|
| corpus_metadata.csv  | CORPUS_METADATA_TNG  | The index and metadata about each of the documents (date, upheld, industry etc.)  |
| complaints_tfidf.csv  | COMPLAINTS_TFIDF_TNG  | Used to generate the wordclouds, it contains the word frequencies (tfidf transformed) for each of the documents  |
| sim_index.csv  | SIM_INDEX_TNG  | The similarity scores of each of the documents to one another (70% similarity minimum to reduce the output data size)  |
| topic_timeseries.csv  | TOPIC_TIMESERIES_TNG  | Alignment of each of the documents with the topics generated by the LDA models  |
| topic_lookup.csv  | TOPIC_LOOKUP_TNG  | For joining onto the timeseries to show the words contained within the topics  |

##### Running the queries
To produce the output tables the following queries need to be run, these can be found in SAS Visual Data Builder. Double click the query and hit the 'run' button. Queries can be found in the following location **Shared Data/SAS Visual Analytics/Public/LASR/FOS scanning/QUERIES**

| Query Name   |Input tables| Output Table Name     | Description  |
| ------------- | ------------- |---------------|---------------|
| QUERY_SIMILARITY_INDEX_TNG  | CORPUS_METADATA_TNG x2, SIM_INDEX_TNG  | SIMILARITY_INDEX_TNG  | Creates the tables with a view of the similarities of the documents, with the metadata joined for each of the docs in the comparison |
| QUERY_LDA_TOPICS_TNG  | TOPIC_TIMESERIES_TNG, CORPUS_METADATA_TNG, TOPIC_LOOKUP_TNG  | LDA_TOPICS_TNG  | Add the document metadata and topic descriptions onto the timeseries data for topic tracking view |
| QUERY_MAIN_WORDCLOUD_TNG  | COMPLAINTS_TFIDF_TNG, CORPUS_METADATA_TNG  | MAIN_WORDCLOUD_TNG  | Adds the metadata onto the word frequency data for SAS VA dashboard |
| QUERY_DOUBLE_SEARCH_TNG | COMPLAINTS_TFIDF_TNG x2, CORPUS_METADATA_TNG | DOUBLE_SEARCH_TNG | This is for the double drill down search |

**Note: Here's a kooky one for you, the QUERY_DOUBLE_SEARCH_TNG may fail, WHY DOES IT FAIL? Well, you need to change the order in the 'Joins' tab of the query and then run it. Don't ask me why, I'm not around anymore.**

##### Updating the report
Enter the report in Report Designer view (located at **Shared Data/Demo/Reports/FOS Scanning v2 TNG**).
1. Update all of the date sliders to include the latest date
1. Each of the external URL links will need to be reset (due to a SAS VA bug). These can be found in the 'Interactions' tab, links need to be updated from 'http:' to 'http:\\\\' (two backslashes)

##### Restarting after LASR crash
As the queries create tables just in LASR memory, these are lost when the server restarts. So you will need to run the queries again. Until LASR issues resolved, only run these 3:

QUERY_LDA_TOPICS_TNG
QUERY_MAIN_WORDCLOUD_TNG
QUERY_SIMILARITY_INDEX_TNG

It shouldn't need to have the tables reloaded but if it does then upload the tables again as above. If you have trouble downloading from Bluemix (I did) then here are my latest ones:

http://hdmduv001a.machine.test.group/keith/

## <a name="theory"></a>Theory
*[gensim](https://radimrehurek.com/gensim/index.html)

## <a name="contribute"></a>Contribute
We are always open to hearing suggestions on how things can be improved. For new features or bugs, feel free to log on this GitHub or better yet submit your ideas and fixes in the form of fully functional code!
