import PyPDF2
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
import string
import time
import pandas as pd
import os
import nltk

# Re-point the nltk_data
nltk.data.path.append("./scraper/nltk_data")
print(nltk.data.path)

def clean(doc):
    """Function to clean up the raw text from a document"""
    exclude = set(string.punctuation)
    # Include additional stopwords
    ignore_words = ['mr',"mrs",'miss', 'also', 'would', 'could', 'may', 'whether', 'however', 'annex', 'chapter', 'appendix', 'footnote',"n't"]
    lemma = WordNetLemmatizer()
    stop = set(stopwords.words('english'))
    stop.update(['ł']+ignore_words)
    doc = doc.replace('™',"'")
    doc = doc.replace('.',". ")
    doc = doc.replace('?',"")
    #print(doc)
    tokens=word_tokenize(doc)
    punc_free = [x for x in tokens if x not in exclude]
    stop_free = [i.lower() for i in punc_free if i.lower() not in stop]
    #print(punc_free)
    # Get rid of bad fullstops
    split_out = [word.split(".") for word in stop_free]
    norm2 = sum(split_out, [])
    normalized = [lemma.lemmatize(word) for word in norm2]
    # Get rid of apostrophe words
    apos_norm = [x for x in normalized if len(x) > 1 and x[0] != "'" ]
    
    return apos_norm

def create_corpus(pdf_response):
    '''From a list of pdf web responses create a corpus of texts to analyse'''
    bad_decrypt = 0
    readable_file = True
    file_name = 'viewPDF'+str(time.time())+'.pdf'
    # Write response to temporary local pdf file
    with open(file_name,'wb') as f:
        f.write(pdf_response.content)
        f.close()

    # Read the pdf into memory using PyPDF2 module
    with open(file_name,'rb') as pdfFileObj:
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    
        # If PDF is encrypted try to decrypt
        if pdfReader.isEncrypted:
            try:
                pdfReader._override_encryption = True
                pdfReader.decrypt('')
                readable_file = True
            except:
                readable_file = False
                bad_decrypt += 1
    
        if readable_file:
            #mentioned_source = dict(zip(sourcebooks, [0]*len(sourcebooks)))
    
            initialize = pdfReader.getPage(0).extractText()
            pdf_pages = pdfReader.flattenedPages
            #try:
            pdf_all = ''
            for page in pdf_pages:
                try:
                    pdf_all = pdf_all + page.extractText()
                except:
                    print('page corrupt')

        #pdf_all_1 = pdf_all.replace('\n', ' ').lower()
        
        pdf_all_tk = clean(pdf_all)
        meta_data = pd.Series(pdfReader.getDocumentInfo())
        meta_data.index = [x[1::] for x in meta_data.index.tolist()]
#        with open('./texts/'+meta_data['Title']+'.txt', 'w') as raw_file:
#            print(str(pdf_all), type(pdf_all.encode(sys.stdout.encoding, 'strict')))
#            raw_file.write(str(pdf_all))
        pdfFileObj.close()
    try:
        os.remove(file_name)
    except:
        print("locked")
    return pdf_all_tk, meta_data, pdf_all.replace('™',"'")