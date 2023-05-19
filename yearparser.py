import sys
import os
import json
import re
from datetime import datetime
import time
import collections
from tqdm import tqdm

"""
This is a script that contains a function to create, 
from these downloaded files, ajson file which contains
a non-redundant set of pubmed records.
It also creates a json file containing the MESH terms-and the PMIDs that each term appears in.
This code is duplicated so it creates files with MESH symbol value-pmids pairs. (ex: journals-pmids,
publication country-pmids, & journal-pmids )

"""
"""""
Useful website: https://www.nlm.nih.gov/bsd/mms/medlineelements.html
Stuff to fix:
# What happens with revised versions of the same article?-revised versions have the same PMID! 
# May need to use PHST- <date> [pubmed] to get a more recent year
#adjust output name?
# This probably can't handle subfolders at the moment
# Right now it has only been tested with parser3.py and the folder in the same
spot. Needs further testing there
#add a part where it can get a pubMed element key as an argument, and then add it to subdata? 
"""""

def getElement(element, line, dictElement, keyName):
    element = element + "  - "
    EL = line.split(element)[-1].rstrip()
    try: #if dictElement[keyName] is a list []
        dictElement[keyName].append(EL) 
    except AttributeError: #elif dictElement[keyName] is a str ""
         if dictElement[keyName] is not "":   
              dictElement[keyName] += (" " +EL)
         else:
            dictElement[keyName] = EL     
    return dictElement
"""^this function takes the pubMed element name, splits it from the line,
     and adds the element value into the dictionary. this does mean there can be cases like
     "abstract":[] in the json. 
"""
def getElementAppearances(element, line, dictElement, docID):
    element = element+ "  - "
    elementLine = line.split(element)[-1].rstrip()
    if elementLine not in dictElement:
        docString = []
        docString.append(docID)
        dictElement[elementLine] = docString
    else:
        dictElement[elementLine].append(docID)
    return dictElement
def parserPubmed(folder_name, source):
    t0= time.clock() #test code efficiency
    if len(folder_name) < 2 or len(source) < 2:
        #if you didn't put a folder name here, spit out an error
        print("Error: parserPubmed(<folder_name>, <source>) is missing a value")
        sys.exit()
    #folder_name = sys.argv[1]
    #^ get folder name from command line
    folder_abs = os.path.abspath(folder_name) #!!There may need to be edits to the code if it can't find the folder!
    print(folder_abs)
    if not os.path.isdir(folder_abs):
        print("Error: The specified folder does not exist.")
        sys.exit()
    #There's an issue with json where you annoyingly need the abspath to write a json file
    output_dir = os.path.abspath(folder_name)

    #folder = os.path.dirname(folder_name)
    folder =os.path.basename(folder_name)
    for filename in os.listdir(folder_name):
        if filename.endswith(".txt"):
            filelabel = filename.split(".")[0]
            PMIDcount = 0 
            docIDcount = 0
            repeatCount = 0
            pmidList = [int]
            PMID = ""
            docID = 0
            data = {}
            #
            try:
                with open(os.path.join(folder_name, filename), "r", encoding="utf8") as f:
                    terms = collections.defaultdict(list)
                    publicationPlaces=collections.defaultdict(list)
                    journals= collections.defaultdict(list)
                    abstracts = collections.defaultdict(list)
                    titles = collections.defaultdict(list)
                    years = collections.defaultdict(list)
                    print (folder)
                    print(filename)
                    #After the first line, each line in the abstract starts with extra spaces.
                    #removing them and the \n character puts the abstract together. 
                    for line in f:
                        line = line.replace("\n      ", "")
                        if line.startswith("PMID-"):
                                PMID = (line.split("- ")[-1])
                                docID= PMID #docID seems to be the same as PMID in this case
                                subdata = {"docid": docID, "pmid": PMID,"year": "",
                                "journal": [], "source": source, "title": "", "abstract" : "",
                                "MeSH Headings": [], "Place of Publication": ""}
                                if docID in data:
                                     repeatCount+=1
                                else:
                                     PMIDcount +=1
                                     #pmidList.append(docID)
                                #Each article gets a subdata dictionary, then its nested into data
                        elif line.startswith("DP  -"): #DP= date published. Note that theyre are several pubmed elements
                            # refering to different dates for the article.
                            #-could be cleaner, and I'm worried about this line potentially failing if the date
                            #is formatted incorrectly
                                DP = line.split("DP  - ")[-1]
                                year1 = int(DP[:4])
                                subdata["year"] = year1
                                if year1 not in years:
                                    docString = []
                                    docString.append(docID)
                                    years[year1] = docString
                                else:
                                    years[year1].append(docID)
                        #elif line starts with the PubMed element key, then run getElement on the line
                        elif line == "":
                             data[docID] = [subdata]
                    
            except OSError as e:
                print("Error opening file:", e)
                sys.exit()
            try:
                os.makedirs(output_dir, exist_ok=True)
                #with open(filelabel+".json", "w", encoding ="utf8") as f:
                for docID in data:
                    docIDcount+=1
                         #json.dump(data[docID], f)
                    #^this for loop is to make sure the output is formatted correctly. 
                    print("Number of PMIDs found:", PMIDcount)
                    print("Number of docIDs added to json", docIDcount)
                    print("Number of repeat docIDs, found:", repeatCount)
                f.close()
               
                with open (os.path.join(folder_name, filelabel+"_years.json"), "w", encoding="utf8") as file7:
                    for yearx in years:
                        y_string= (f"{yearx, years[yearx]} total:{len(years[yearx])}")
                        json.dump([y_string], file7)
                file7.close()
                t1 = time.clock()
                print("Time elapsed: ", t1 - t0)
            except OSError as e:
                print("Error writing to file:", e)
                sys.exit()

parserPubmed("medline", "medline")