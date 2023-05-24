from pickle import FALSE
import sys
import os
import json
import re
from datetime import datetime
import time
import collections
from tqdm.auto import tqdm
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
            #filesize = os.path.getsize(os.path.join(folder_name, filename))
            try:
                print("\n")
                with open(os.path.join(folder_name, filename), "r", encoding="utf8") as f:
                    #print (folder)
                    print(filename)
                    terms = collections.defaultdict(list)
                    publicationPlaces=collections.defaultdict(list)
                    journals= collections.defaultdict(list)
                    abstracts = collections.defaultdict(str)
                    titles = collections.defaultdict(str)
                    years = collections.defaultdict(list)
                # ABflag = 0
                    TitleFlag = 0
                    JournalFlag = 0
                    
                    #After the first line, each line in the abstract starts with extra spaces.
                    #removing them and the \n character puts the abstract together.
                    filesize =sum(1 for i in open(os.path.join(folder_name, filename), 'rb'))
                    print(filesize)
                    with tqdm(total= filesize) as pbar:
                        for line in f:
                            line = line.replace("\n", "")
                            line = line.replace("      ", "")
                            if (" - ") in line:
                                #ABflag = 0
                                TitleFlag = 0
                                JournalFlag = 0
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
                            elif line.startswith("TA  -"):
                                TA =getElement("TA", line, subdata, "journal")
                                TA2= getElementAppearances("TA", line, journals, docID)
                            elif line.startswith("TI  -"):
                                TI =getElement("TI", line, subdata, "title")
                                TI2 = getElement("TI", line, titles, PMID)
                                TitleFlag = 1
                            elif line != "" and TitleFlag == 1:
                                titles[PMID] = str(titles[PMID] +line)
                                subdata["title"] = str(subdata["title"] + line)
                            elif line.startswith("PL  -"):
                                PL = getElement("PL", line, subdata, "Place of Publication")
                                PL2=  getElementAppearances("PL", line, publicationPlaces, docID)
                            elif line.startswith("MH  -"):
                                MH = getElement("MH", line, subdata, "MeSH Headings")
                                MH2= getElementAppearances("MH", line, terms, docID)
                            elif line == "":
                                data[docID] = [subdata]
                            """
                            elif line.startswith("AB  -"):
                                AB = getElement("AB", line, subdata, "abstract")
                                AB2= getElement("TI", line, abstracts, PMID)
                                ABflag = 1
                            elif line != "" and ABflag == 1:
                                abstracts[PMID] = str(abstracts[PMID] +line)
                                subdata["abstract"] += line
                            """
                    data[docID] = [subdata]
            except OSError as e:
                print("Error opening file:", e)
                sys.exit()

            f.close()      
            try:
                os.makedirs(output_dir, exist_ok=True)
                #os.makedirs(output_dir+"\\totals", exist_ok=True)
                #with open(filelabel+".json", "w", encoding ="utf8") as f:
                for docID in data:
                    docIDcount+=1
                titleTest = 0
                for docID in titles:
                    titleTest +=1
                         #json.dump(data[docID], f)
                    #^this for loop is to make sure the output is formatted correctly. 
                print("Number of PMIDs found:", PMIDcount)
                print("Number of docIDs added to json", docIDcount)
                print("Number of repeat docIDs, found:", repeatCount)
                print("Number of titles found:", titleTest)
                f.close()
                with open (os.path.join(folder_name, filelabel+"_terms.json"), "w", encoding="utf8") as file2:
                    for term in terms:
                        termstring= (f"{term, terms[term]} total:{len(terms[term])}")
                        json.dump([termstring], file2)
                file2.close()
                with open (os.path.join(folder_name+"\\totals", filelabel+"_total_terms.json"), "w", encoding="utf8") as file2_total:
                    for term in terms:
                        termstring= (f"{term}, {len(terms[term])}")
                        json.dump([termstring], file2_total)
                file2_total.close()
                with open (os.path.join(folder_name, filelabel+"_countries.json"), "w", encoding="utf8") as file3:
                    for place in publicationPlaces:
                        c_string= (f"{place, publicationPlaces[place]} total:{len(publicationPlaces[place])}")
                        json.dump(c_string, file3)
                file3.close()
                with open (os.path.join(folder_name+"\\totals", filelabel+"_total_Places.json"), "w", encoding="utf8") as file3_total:
                    for place in publicationPlaces:
                        p_string= (f"{place}, {len(publicationPlaces[place])}")
                        json.dump([p_string], file3_total)
                file3_total.close()
                with open (os.path.join(folder_name, filelabel+"_journals.json"), "w", encoding="utf8") as file4:
                    for journal in journals:
                        j_string= (f"{journal, journals[journal]} total:{len(journals[journal])}")
                        json.dump([j_string], file4)
                file4.close()
                with open (os.path.join(folder_name+"\\totals", filelabel+"_total_journals.json"), "w", encoding="utf8") as file4_total:
                    for journal in journals:
                        journalstring= (f"{journal}, {len(journals[journal])}")
                        json.dump([journalstring], file4_total)
                file4_total.close()
                """
                with open (os.path.join(folder_name, filelabel+"_titles.json"), "w", encoding="utf8") as file5:
                    for title in titles:
                        t_string= (f"{title, titles[title]} total:{len(titles[title])}")
                        json.dump([t_string], file5)
                file5.close()
                with open (os.path.join(folder_name, filelabel+"_abstracts.json"), "w", encoding="utf8") as file6:
                    for abstract in abstracts:
                        ab_string= (f"{abstract, abstracts[abstract]} total:{len(abstracts[abstract])}")
                        json.dump([ab_string], file6)
                file6.close()
                """
                with open (os.path.join(folder_name, filelabel+"_years.json"), "w", encoding="utf8") as file7:
                    for yearx in years:
                        y_string= (f"{yearx, years[yearx]} total:{len(years[yearx])}")
                        json.dump([y_string], file7)
                file7.close()
                with open (os.path.join(folder_name+"\\totals", filelabel+"totals_years.json"), "w", encoding="utf8") as file7_totals:
                    for yearx in years:
                        y_string= (f"{yearx} total:{len(years[yearx])}")
                        json.dump([y_string], file7_totals)
                file7_totals.close()
                t1 = time.clock()
                print("Time elapsed: ", t1 - t0)
            except OSError as e:
                print("Error writing to file:", e)
                sys.exit()
    # with open (pmidListdoc, "w", encoding ="utf8") as fp:
    #     for item in pmidList:
    #         fp.write("%s\n" % item)
    #     print("done")
    #     fp.close()
    #     print(len(pmidList))
    #print(len(data))
#example run of parsePubmed. likely the folder path needs to be more specific
#at this time, both brca1 & parser3 are in the same folder
parserPubmed("medline", "medline")