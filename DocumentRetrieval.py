import re
import xml.etree.ElementTree as ET
import warnings
import math
from stemming.porter2 import stem
import pandas as pd


# preprocessing method
def string_tokenise(string):  # return list
    result = re.findall(r"\w+", string)
    return result


def case_fold(list1):  # return list
    result = [word.lower() for word in list1]
    #     string = ' '.join([str(elem) for elem in list1])
    #     result = string.lower().split() #lower() is the same as casefold()
    return result


def stopping(list1):  # return list
    stopfile = open("englishST.txt", 'r')
    stopwords = stopfile.read().split()
    result = [items for items in list1 if items not in stopwords]
    return result


def normalise(list1):  # return list
    result = []
    for item in list1:
        result.append(stem(item))
    return result


'''
Search function1: single search function
return list containing the docID
eg. single_search('Window',2)
'''
def single_search(single_query_str, query_id):
    result = []  # define the return value
    query_term = normalise(
        stopping(case_fold(string_tokenise(single_query_str))))  # same preprocessing as for indexing

    # handling inappropriate queries
    if len(query_term) < 1:
        raise ValueError('Input improperly')

    elif query_term[0] in record:  # only one element in <query_term>
        for docID in record[query_term[0]]:
            # <record[query_term[0]]> is a dictionary recording {docID:pos in a doc} for given term
            # docID is the key in dictionary{docID:pos in a doc}
            result.append(docID)

    # if no record then will return a empty list, which follows the intuition
    return result


'''
NOT A SEARCH FUNCTION: proximity_core
input: list of term after preprocessing; distance:int ; phase_case is a boolean value indicating the it's a phase search or not
output a list containing the docID
'''
def proximity_core(query_term, distance, phase_case):
    half_result = []  # start from 0; nested list
    result = []
    term_idx = 0  # start from 1

    for term in query_term:
        term_idx = term_idx + 1  # start from 1
        if term in record:
            half_result.append(list(record[term].keys()))  # list append a list which recording the docID
        else:
            continue

    # handle the case that for at least one term cannot match
    if len(half_result) < 2:
        result = []
        return result

    # the case that for all terms can find matches
    common_doc = [common for common in half_result[0] if common in half_result[1]]

    for doc in common_doc:
        flag = 0  # set for indicate matching status

        pos_in_doc1 = re.split(r', ', record[query_term[0]].get(doc))
        pos_in_doc2 = re.split(r', ', record[query_term[1]].get(doc))
        for pos1 in pos_in_doc1:
            if flag == 1:
                break
            for pos2 in pos_in_doc2:
                if phase_case:
                    if int(pos2) - int(pos1) == 1:
                        result.append(doc)
                        flag = 1
                        break
                else:
                    if abs(int(pos1) - int(pos2)) <= distance:
                        result.append(doc)
                        flag = 1
                        break
    return result



'''
Search function2: proximity_search
input: string of query, queryid
output: a list containing [docID]
'''
def proximity_search(query_str, query_id):
    result = []  # returned list
    dist_info = re.compile(r'#[0-9]+').search(
        '#10(income, taxes)').span()  # locate the position of distance info in string
    distance = int(query_str[1:dist_info[1]])  # extract the distance info
    query_term = normalise(
        stopping(case_fold(string_tokenise(query_str[dist_info[1] + 1:]))))  # same preprocessing as for indexing

    # handling inappropriate queries
    if len(query_term) == 1:
        result = single_search(str(query_term), query_id)
        warnings.warn(
            "\n  Input improperly! \n  Note the search result doesn't meet the positional reqirement.\n")
        return result
    elif len(query_term) == 0:
        raise ValueError('Input improperly')

    # proper input case
    else:
        result = proximity_core(query_term, distance, phase_case=False)
        return result


'''
Search function3: phase_search
input: string of query, queryid
output: a list containing [docID]
'''
def phase_search(query_str, query_id):
    result = []  # returned list
    query_term = normalise(
        stopping(case_fold(string_tokenise(query_str))))  # same preprocessing as for indexing

    # handling inappropriate queries
    if len(query_term) == 1:
        result = single_search(str(query_term), query_id)
        return result
    elif len(query_term) == 0:
        raise ValueError('Input improperly!')

    else:
        result = proximity_core(query_term, distance=1, phase_case=True)

    return result


'''
Search function4: boolean search function
return list containing the docID
eg. single_search('Window',2)
'''
def boolean_search(query_str, query_id):
    # identify the boolean operator
    if re.compile(r'\bAND NOT\b').search(query_str):
        query_partial = re.split(r'\bAND NOT\b', query_str)
        operator = 'AND NOT'
    elif re.compile(r'\bOR NOT\b').search(query_str):
        query_partial = re.split(r'\bOR NOT\b', query_str)
        operator = 'OR NOT'
    elif re.compile(r'\bOR\b').search(query_str):
        query_partial = re.split(r'\bOR\b', query_str)
        operator = 'OR'
    elif re.compile(r'\bAND\b').search(query_str):
        query_partial = re.split(r'\bAND\b', query_str)
        operator = 'AND'

    half_result = []  # list of the search result of each partial instead of the whole query (idx from 0)
    # structure: nested list
    result = []  # the returned list of this function
    part_idx = 0  # idx of the partial of boolean query (1 or 2)

    for part in query_partial:  # every part of the boolean expression
        part_idx = part_idx + 1

        # handle the improper imput
        if len(string_tokenise(part)) == 0:
            raise ValueError('Input improperly!')

        if len(string_tokenise(part)) == 1:  # before the preprocessing bsc normalise twice maybe harm the result
            half_result.append(single_search(str(string_tokenise(part)), query_id))
            # No preprocessing here, for preprocessing is embeded in individual search function
        if len(string_tokenise(part)) > 1:
            half_result.append(phase_search(query_str=part, query_id=query_id))

    if operator == "AND NOT":
        result = [items for items in half_result[0] if items not in half_result[1]]

    elif operator == "OR NOT":
        result = [items for items in docID_list if (items not in half_result[1]) or (items in half_result[0])]

    elif operator == 'AND':
        result = [items for items in half_result[0] if items in half_result[1]]

    elif operator == 'OR':
        result = [items for items in docID_list if (items in half_result[0]) or (items in half_result[1])]

    return result



'''
=======================================Preparation: indexing======================================
'''

IndexingOutput = open('database_content_indexing.txt', 'w')  # save the result
englishST = open('englishST.txt', 'r')

FILE = 'PoynterCovid19Database_Reference_Article.csv'

record = {}  # {{string:{int:string}}} {{term:{docID:position}}}dic of dic, every insider dic records a term
docID_list = []  # list just for recording docID

fields = ['docID','content', 'accuracy', 'date', 'region', 'explanation', 'reference_url', 'reference_html', 'reference_text']
dataframe = pd.read_csv(FILE, usecols = fields)

docID = 0

for index, row in dataframe.iterrows():

    docID = row['docID']
    docID_list.append(docID)

    # step1: tokenise
    doc_in_str = row['content'] # doc is in string format
    pos_in_doc = 0  # describe the position of terms in one doc

    term_in_list = normalise(
        stopping(case_fold(string_tokenise(doc_in_str))))  # pre-processing

    # step2: for each term, record the position in record[term]
    for term in term_in_list:
        pos_in_doc = pos_in_doc + 1
        if term not in record:  # if this term has not shown before
            record[term] = {docID: str(pos_in_doc)}  # add an entry in record
        else:
            # if this docID has been recorded in <record>
            if docID in record[term]:
                record[term][docID] = record[term].get(
                    docID) + ", " + str(pos_in_doc)  # add one more postition
            else:  # term appers in a new doc
                record[term][docID] = str(pos_in_doc)


# Sort the record by alphabetical order
sorted_term_list = sorted(record)

# Write into output txt file
for entry in sorted_term_list:
    IndexingOutput.write(str(entry) + ':' + str(len(record[entry])) + '\n')  # term:df
    for docid in record[entry].keys():
        IndexingOutput.write('\t' + str(docid) + ': ' + record[entry].get(docid) + '\n')  # docID: pos1, pos2, ...

num_of_doc = docID + 1 # the total number of entries in the dataset

IndexingOutput.close()


'''
========================================Document Retrieval=======================================
'''
query_id = 0
RankedIROutput = open('document_retrieval_results.txt', 'w')

# step1: extract the original queries from file
query_ranked_file = open("queries_toy.txt", "r")
query_ranked_str = query_ranked_file.read()
query_ranked_list = re.split(r'\n', query_ranked_str)

i = 0;
for query in query_ranked_list:
    query_ranked_list[i] = query_ranked_list[i][:-1]
    i = i + 1       # turn the file into the format we want

for query in query_ranked_list:
    query_id = query_id + 1  # according to file, query index starts from 1
    subscore = {}  # structure: nested dict, for each term in query,{{term1:{docID:subscore}},{term2:...}
    query_term = normalise(
        stopping(case_fold(string_tokenise(query))))  # same preprocessing as for indexing
    for term in query_term:
        if term in record:
            doc_list = list(record[term].keys())
            for doc in doc_list:
                tf = len(re.split(r', ', record[term].get(doc)))
                df = len(doc_list)
                N = len(docID_list) # the total number of entries in the dataset
                # print(str(tf),str(df),str(N))
                if term in subscore:  # can only add one level of dictionary at a time
                    subscore[term][doc] = (1 + math.log10(tf)) * math.log10(N / df)  # calculate subscore for each term
                else:
                    subscore[term] = {
                        doc: (1 + math.log10(tf)) * math.log10(N / df)}  # calculate subscore for each term
        else:
            continue

    # handle the case that cannot find any matches
    if subscore == []:
        search_result = []

    # calculate the score of each doc for this query
    else:
        doc_score = {}  # structure: dictionary{docID:score}
        for term in list(subscore.keys()):
            for doc in list(subscore[term].keys()):
                if doc in list(doc_score.keys()):
                    doc_score[doc] = doc_score.get(doc) + subscore[term].get(doc)
                else:
                    doc_score[doc] = subscore[term].get(doc)

    # get the doc_score sorted
    search_result = sorted(doc_score.items(), key=lambda x: x[1], reverse=True)  # nested list: [[docID,score]...]

    # write into submitted file
    count = 0  # provide up to 150 result
    for matched_entry in search_result:
        count = count + 1
        if count > 10:
            break
        RankedIROutput.write(str(query_id) + ',' + str(matched_entry[0]) + ',' + str(round(matched_entry[1],4)) +
                            ' ||' + dataframe.loc[dataframe['docID']==matched_entry[0]]['content'].item() + '\n')

RankedIROutput.close()