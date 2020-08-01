from os import listdir
from os.path import isfile, join,isdir
import sys
import json
from html.parser import HTMLParser
from collections import defaultdict
from bs4 import BeautifulSoup
import math
import ast
import time
from pprint import pprint

urlID = dict()
partial_indexes = ['partial1.json','partial2.json', 'partial3.json']
partial = 0
num_files = 0
length_squared_vector = defaultdict(int)

class Posting:

    def __init__(self,ID, terms):
        self.ID = ID
        self.frequency = 1
        self.total_terms = terms
        self.tf = 0
        self.idf = 0
        self.tfidf = 0

    def __str__(self):
        return f'ID: {self.ID}, frequency: {self.frequency}, total_terms: {self.total_terms}, tfidf: {self.tfidf}, tf: {self.tf}, idf: {self.idf}'
        
class CustomEncoder(json.JSONEncoder):
    
    def default(self, o):
        return {'__{}__'.format(o.__class__.__name__): o.__dict__}


def remove_html_tags(text):
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def get_files(mypath):
    global partial
    global num_files
    global length_squared_vector
    onlyfiles = []
    allwords = defaultdict(list)
 #   allwords = defaultdict(lambda : defaultdict(list))
 
    if (isdir(mypath)):
        for i in listdir(mypath):
            print(i)
            if (isdir(join(mypath, i))):
                for j in listdir(join(mypath, i)):
                    num_files += 1
                     # Convert URLs to ID
                    file = open(join(mypath,i,j),'r')
                    data = json.load(file)
                    url = data['url']
                    urlID[num_files] = url
                    content = data['content']
                    file.close()
                    soup = BeautifulSoup(content, features = 'html.parser')
                    for script in soup(["script","style"]):
                        script.extract()    
                    text = soup.get_text()
    ##                print('--------- TEXT _________')
    ##                print(text)
    ##                content = remove_html_tags(content)
    ##                print('--------- CONTENT _________')
    ##                print(content)
                    words = text.strip().lower().split()
                    alnum = [word for word in words if word.isalnum()]
                    total_terms = len(alnum)
                    for word in alnum:
                        if word not in allwords:
                            allwords[word].append(Posting(num_files, total_terms))
                        else:
                            if allwords[word][-1].ID != num_files:
                                allwords[word].append(Posting(num_files, total_terms))
                            else:
                                allwords[word][-1].frequency += 1

    ##########################################################################################
##                    if num_files == 41:
##                        break
                    if num_files == 20:
                        index1 = open(partial_indexes[partial], 'w')
                        index_content = json.dumps(allwords, cls = CustomEncoder)
                        index1.write(index_content)
##                        index1.write(str(dict(allwords)))
                        partial += 1
                        index1.close()
                        allwords = defaultdict(list)
                    elif num_files == 40:
                        index1 = open(partial_indexes[partial], 'w')
                        index_content = json.dumps(allwords, cls = CustomEncoder)
                        index1.write(index_content)
##                        index1.write(str(dict(allwords)))
                        partial += 1
                        index1.close()
                        allwords = defaultdict(list)
##            break
    index1 = open(partial_indexes[partial], 'w')
    index_content = json.dumps(allwords, cls = CustomEncoder)
    index1.write(index_content)
 #   index1.write(str(dict(allwords)))
    partial += 1
    index1.close()
##    
##    index1 = open("test.json" , 'w')
##    index1.write(str({'str' : [12,13], 'wer' : [15,17]}))
##    index1.close()
##                for term in allwords:
##                    for posting in allwords[term]:
##                        if posting.ID == num_files:
##                            posting.total_terms = total_terms
##                if num_files == 5:
##                    break
##            break
                        
    for term in allwords:   
##        print(term)
        for posting in allwords[term]:
            posting.tf = 1 + math.log(posting.frequency, 10)
            posting.idf = math.log((num_files/len(allwords[term])), 10)
            posting.tfidf = posting.tf * posting.idf
            length_squared_vector[posting.ID] += posting.tfidf**2
##            print(f'[{posting}]',end = '')
##        print()
    
    return dict(allwords)

##def search_index(index, query) -> [Posting]:
##    query = query.strip().lower().split()
##    urls = []
##    if len(query) == 1:
##        try:
##            postings = index[query]
##        except KeyError:
##            return []
##        for i in postings:
##            urls.append(i.ID)
##        return urls
##    elif query > 1:
##        num = 0
##        for i in query:
##            if i in index:
##                for posting in index[i]:
##                    urlid = posting.ID
##                    for j in posting.positions:
##                        for x in index[query[num+1]]:
##
##def search_index(index, query) -> list:
##    query = query.strip().lower().split()
##    urls = []
##    if len(query) == 1:
##        if (query[0] in index):
##            return index[query[0]].keys()
##    elif len(query) > 1:
##        query_index = 0
##        for i in query[1]:
##            if i in index:
##                for doc in index[i]:
##                    for num in index[i][doc]:
##                        if (num+1 in index[query[1]][doc]):
##                            urls.append(doc)
##                            break
##    return urls

def cosine_similarity(query, docs):
    scores = defaultdict(int)
    squared_query_tfidf = 0
    for i in set(query):
    #    q_tf = 1 + math.log(query.count(i)/len(query), 10)
        q_tf = query.count(i)
        try:
            q_idf = math.log((num_files) / len(docs[i]), 10)
        except KeyError:
            continue
        q_tfidf = q_tf*q_idf
        squared_query_tfidf += q_tfidf**2
        for posting in docs[i]:
            scores[posting.ID] +=  q_tfidf*posting.tfidf
    length_query = math.sqrt(squared_query_tfidf)
    for doc in scores:
        length_doc = math.sqrt(length_squared_vector[doc])
        scores[doc] = scores[doc]/(length_doc*length_query)        
    return scores

def new_cosine_similarity(query, docs):
    scores = defaultdict(int)
    squared_query_tfidf = 0
    for i in set(query):
        q_tf = query.count(i)
        if i in docs:
            q_idf = math.log((num_files) / len(docs[i]), 10)
        else:
            continue
        q_tfidf = q_tf*q_idf
        squared_query_tfidf += q_tfidf**2
        for posting in docs[i]:
            scores[posting['__Posting__']['ID']] +=  q_tfidf*posting['__Posting__']['tfidf']
    length_query = math.sqrt(squared_query_tfidf)
    for doc in scores:
        length_doc = math.sqrt(length_squared_vector[doc])
        scores[doc] = scores[doc]/(length_doc*length_query)        
    return scores

def new_cosine_similarity2(query, docs):
    scores = defaultdict(int)
    squared_query_tfidf = 0
    first = []
    second = []
    third = []
    for i in set(query):
        if 'a' <= i[0] <= 'i':
            first.append(i)
        elif 'j' <= i[0] <= 'r':
            second.append(i)
        else:
            third.append(i)
    
    for i in set(query):
        if 'a' <= i[0] <= 'i':
            file = open(partial_indexes[0], 'r')
        elif 'j' <= i[0] <= 'r':
            file = open(partial_indexes[1], 'r')
        else:
            file = open(partial_indexes[1], 'r')
    #    q_tf = 1 + math.log(query.count(i)/len(query), 10)
        q_tf = query.count(i)
        try:
            q_idf = math.log((num_files) / len(docs[i]), 10)
        except KeyError:
            continue
        q_tfidf = q_tf*q_idf
        squared_query_tfidf += q_tfidf**2
        for posting in docs[i]:
            scores[posting['__Posting__']['ID']] +=  q_tfidf*posting['__Posting__']['tfidf']
    length_query = math.sqrt(squared_query_tfidf)
    for doc in scores:
        length_doc = math.sqrt(length_squared_vector[doc])
        scores[doc] = scores[doc]/(length_doc*length_query)        
    return scores

def read_files():
    count = 0
    merged = defaultdict(list)
    for i in partial_indexes:
        file = open(i,'r').read()
        if count == 0:
            index1 =  json.loads(file)
            for key in index1:
                merged[key].extend(index1[key])
            count += 1
        elif count == 1:
            index2 =  json.loads(file)
            for key in index2:
                merged[key].extend(index2[key])
            count += 1
        elif count == 2:
            index3 =  json.loads(file)
            for key in index3:
                merged[key].extend(index3[key])
    calculate_tfidf(merged)
    
    mergedfile = open('merged_index.json', 'w')
    merged_content = json.dumps(merged, cls = CustomEncoder)
    mergedfile.write(merged_content)

    return merged    

def sort_write_merged(merged):
    index1 = defaultdict(list)
    index2 = defaultdict(list) 
    index3 = defaultdict(list)
    for i in merged.keys():
        if 'a' <= i[0] <= 'i':
            index1[i] = merged[i]
        elif 'j' <= i[0] <= 'r':
            index2[i] = merged[i]
        else:
            index3[i] = merged[i]
    count = 0
    for file in partial_indexes:
        f = open(file,'w')
        if count == 0:
            f.write(str(dict(index1)))
            count += 1
        elif count == 1:
            f.write(str(dict(index2)))
            count += 1
        elif count == 2:
            f.write(str(dict(index3)))
    return
              
            

def calculate_tfidf(allwords):
    for term in allwords:   
##        print(term)
        for posting in allwords[term]:
            posting['__Posting__']['tf'] = 1 + math.log(posting['__Posting__']['frequency'], 10)
            posting['__Posting__']['idf'] = math.log((num_files/len(allwords[term])), 10)
            posting['__Posting__']['tfidf'] = posting['__Posting__']['tf'] * posting['__Posting__']['idf']
            length_squared_vector[posting['__Posting__']['ID']] += posting['__Posting__']['tfidf']**2

if __name__ == '__main__':
    
    print("Indexing files...")    
    invIndex = get_files(sys.argv[1])
    merged_docs = read_files()
    print("Indexing complete.")
    
    while True:
        query = input("\nEnter search query:").strip().lower()
        if query == 'exit':
            break
        start = time.time()
        all_scores = new_cosine_similarity(query.split(), merged_docs)
        end = time.time()
        print(f'Query response time: {end-start} seconds.\n')
        topdocs = sorted(all_scores.keys(), key = lambda x: all_scores[x], reverse = True)
        if len(topdocs) == 0:
            print('No matches found.')
            continue
        topn = len(topdocs) if len(topdocs) < 10 else 10
        print(f'\nTop {topn} documents:\n')
        for i in range(topn): 
            print(f'{urlID[topdocs[i]]}: {all_scores[topdocs[i]]}')
        
