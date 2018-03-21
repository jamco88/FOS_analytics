# Financial Ombudsman Service Complaints Analytics
Data analysis developed by Risk Innovation team to discover trends in Financial Ombudsman Complaints data to give better legal over site of emerging threats.

The application runs in Cloud Foundry on the LBG sandbox - currently in the DEV environment ([RI face recognition](https://raft-face-recognition.lbg.eu-gb.mybluemix.net/))<hr></hr>

The flat files produced are then surfaced in an interactive SAS Visual Analytics report which allows users to explore to corpus in a number of different ways, with the overlay of text analytics.

## <a name="team-members"></a>Table of Contents
* [Team Members](#team-members)
* [Background](#background)
* [Getting Started](#get-started)
* [Theory](#theory)
* [Contribute](#contribute)

## <a name="team-members"></a>Team Members
#### Development
* "Sven Harris" <sven.harris@lloydsbanking.com>
* "Jack Grimes" <jack.grimes@lloydsbanking.com>
* "Gordon Baggott" <gordon.baggott@lloydsbanking.com>

#### Business Stakeholders
* "Tricia McGrath" <patricia.mcgrath@lloydsbanking.co.uk> - Legal Developments, Group Legal
* "Jacqueline Lawrence" <Jacqueline.JB.Lawrence@lloydsbanking.com> - Legal Developments, Group Legal

## <a name="background"></a>Background
Teams in Group Legal are required to understand the external legal and regulatory environments and spot trends or patterns that may come to materially impact the group (e.g. PPI). The Financial Ombudsman Service publishes complaints on which it makes decisions whether or not to uphold, and the remediatory required to be taken by the company involved. This is a rich source of information about consumer trends, and potential compliance risks, however the volumes of complaints mean it is unfeasible to capture and understand all of this information by reading all of the complaint releases (the corpus contains over 100,000 documents).

This motivated the development of an application with which the high level trends can be abstracted, still with the capability to drill down and aggregate by different filters as well as access the original complaint documents.

## <a name="get-started"></a>Running the Process

#### Requirements
To run the app locally you need to first clone the code from github by running the following command in git cmd

`git clone https://github.lbg.eu-gb.bluemix.net/RiskInnovationDataScience/FOS-analytics`

you then need to take a copy of the latest version of the raw data file. This is saved on the Risk Innovation shared drive:

**\\GLOBAL.LLOYDSTSB.COM\FILE2\RISKINNOV\SHARED\RISKINNOV\1. Team Folder\Sven\1707 - FOS tracking\Scraped Data\small_corpus2.json**

*This is a funny file name because it is nearly 1GB in size, but sometimes light relief is welcome*

Copy this data into the `/scraper/scraping_data` folder

#### Scraping the data
To scrape the latest data onto the document:
1. Open up the scraper script `/scraper/scraper.py`
1. Go to [the Financial Ombudsman Website](http://www.ombudsman-decisions.org.uk/) and find the latest complaint published using the search function
1. Look at the URL of the complaint and note down the number in `viewPDF.aspx?FileID=**XXXXXX**`
1. In the update_corpus function update the `start_no` variable
1. On line 39 change the number `for n in range(start_no, start_no-XXXXX, -1):` to fill in the number of documents you want to retrieve, typically this will to be create the loop going back to the most recently scraped number
1. Run the `update_corpus` function, you will need to enter you GLOBAL password in order to GET the requests through the LBG proxy
1. Wait for the script to complete running, you will see each of the url requests (this will take a little while to start since it first checks for URLs that have already been scraped)

#### Running the analytics
1. Open the `main.py` file
1. Run the `main.py` file (this will take quite long to run [over an hour] since it's training multiple models, so don't run it too late in the day!)
1. Move the CSVs in the `K:\RISKINNOV\1. Team Folder\Sven\1707 - FOS tracking\Output Data` into the archive folder so the last good copy of the data isn't lost
1. Copy the output CSVs in the `/output_data` folder into the `K:\RISKINNOV\1. Team Folder\Sven\1707 - FOS tracking\Output Data` folder

### Updating the report
Each of the tables produced by the Python text analytics needs to be loaded into SAS, queries then need to be run to produce the full tables for the reports. Finally some of the default values should be updated in the report so that everything looks fresh.

##### Loading the tables
The below tables need to be loaded into SAS VA, this can be done in SAS Visual Data Builder (to import File > Import Data...). They need to be uploaded into the following location **Shared Data/SAS Visual Analytics/Public/LASR/FOS scanning/RAW**

**Note: When uploading the TOPIC_TIMESERIES table set rows to scan to 100,000 otherwise some values can become truncated**

| Python Name   | SAS Name      | Description  |
| ------------- | ------------- |---------------|
| corpus_metadata.csv  | CORPUS_METADATA_V2  | The index and metadata about each of the documents (date, upheld, industry etc.)  |
| complaints_tfidf.csv  | COMPLAINTS_TFIDF  | Used to generate the wordclouds, it contains the word frequencies (tfidf transformed) for each of the documents  |
| sim_index.csv  | SIM_INDEXV2  | The similarity scores of each of the documents to one another (70% similarity minimum to reduce the output data size)  |
| topic_timeseries.csv  | TOPIC_TIMESERIES  | Alignment of each of the documents with the topics generated by the LDA models  |
| topic_lookup.csv  | TOPIC_LOOKUP_V2  | For joining onto the timeseries to show the words contained within the topics  |

##### Running the queries
To produce the output tables the following queries need to be run, these can be found in SAS Visual Data Builder. Double click the query and hit the 'run' button. Queries can be found in the following location **Shared Data/SAS Visual Analytics/Public/LASR/FOS scanning/QUERIES**

| Query Name   |Input tables| Output Table Name     | Description  |
| ------------- | ------------- |---------------|---------------|
| SimilarityTables  | CORPUS_METADATA_V2 x2, SIM_INDEXV2  | SimilarDocs_v2  | Creates the tables with a view of the similarities of the documents, with the metadata joined for each of the docs in the comparison |
| QUERY_LDA_TOPICS  | TOPIC_TIMESERIES, CORPUS_METADATA_V2, TOPIC_LOOKUP_V2  | LDA_TOPICS  | Add the document metadata and topic descriptions onto the timeseries data for topic tracking view |
| QUERY_MAIN_WORDCLOUD  | COMPLAINTS_TFIDF, CORPUS_METADATA_V2  | MAIN_WORDCLOUD  | Adds the metadata onto the word frequency data for SAS VA dashboard |

##### Updating the report
Enter the report in Report Designer view (located at **Shared Data/Demo/Reports/FOS Scanning - Jack Full Data**).
1. Update all of the date sliders to include the latest date
1. Each of the external URL links will need to be reset (due to a SAS VA bug). These can be found in the 'Interactions' tab, links need to be updated from 'http:/' to 'http://'

## <a name="theory"></a>Theory
*[gensim](https://radimrehurek.com/gensim/index.html)

## <a name="contribute"></a>Contribute
We are always open to hearing suggestions on how things can be improved. For new features or bugs, feel free to log on this GitHub or better yet submit your ideas and fixes in the form of fully functional code!