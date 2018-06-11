#!/usr/bin/python3
import string
import subprocess
import glob
import pickle
import sys
import math
from operator import attrgetter

def compile_java(java_file):
    subprocess.check_call(['javac', java_file])

def java_stemmer(input):
    #java_class,ext = os.path.splitext(java_file)
    process = subprocess.Popen(['java', 'PorterStemmer', str(input)],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    to_return = process.stdout.read().decode('iso-8859-1').rstrip()
    #print(to_return)
    return to_return

def get_stopwords():
    stopfile = open('stopwords.txt')
    stopwords = stopfile.read()
    stopwords = stopwords.replace('\n', ' ')
    stopwords = stopwords.replace('\t', ' ')
    stopwords = stopwords.split(' ')
    stopset = set()
    stopset.update(stopwords)
    return stopwords

def tokenize_file(filename, stopset):
    infile = open(filename, encoding='iso-8859-1')
    contents = infile.read()
    contents = contents.replace('-',' ')
    contents = contents.replace('\n', ' ')
    contents = contents.replace('\t', ' ')
    contents = contents.replace('  ', ' ')
    contents = contents.rstrip()
    tokens = contents.lower().split(' ')
    tokens = [''.join(c for c in s if c not in string.punctuation) for s in tokens]
    cleaned = list()
    for token in tokens:
        #print(token)
        if token not in stopset:
            cleaned.append(token)
    #print(tokens)
    #print(cleaned)
    return cleaned

def stem_words(to_stem):
    completed_stemmed = list()
    for word in to_stem:
        if word.isalpha():
            stemmed = java_stemmer(word)
            completed_stemmed.append(stemmed)
        else:
            completed_stemmed.append(word)
    # print(completed_stemmed)
    stemmed_set = set()
    stemmed_set.update(completed_stemmed)
    return completed_stemmed, stemmed_set

def main():
    stopset = get_stopwords()
    file_list = glob.glob('To_be_posted/*.txt')
    document_word_count = {}
    index_dict = {}
    print(file_list)
    for file in file_list:
        print("\n\nFile: " + file)
        tokenized = tokenize_file(file, stopset)
        completed_stemmed, stemmed_set = stem_words(tokenized)
        for stemmed in stemmed_set:
            document_word_count[stemmed] = document_word_count.get(stemmed, 0) + 1

        index_dict[file] = dict()
        for word in completed_stemmed:
            index_dict[file][word] = index_dict[file].get(word, 0) + 1

        print(document_word_count)
        print(index_dict[file])

    pickle.dump(document_word_count, open('document_word_count.p', 'wb'))
    pickle.dump(index_dict, open('index_dict.p', 'wb'))

def unpickle():
    document_word_count = pickle.load( open('document_word_count.p', 'rb'))
    index_dict = pickle.load( open('index_dict.p', 'rb'))
    #print(document_word_count)
    #file_list = glob.glob('To_be_posted/*.txt')
    #for file in file_list:
    #    print(index_dict[file])
    return document_word_count, index_dict


def stem_query(query):
    stopwords = get_stopwords()
    stopped = list()
    for word in query:
        if word not in stopwords:
            stopped.append(word)
    stemmed, trash = stem_words(stopped)
    # print(stemmed)
    return stemmed

def get_query(to_query):
    #print(sys.argv[1:])
    original_query = ''
    for word in to_query.split(' '):
        original_query += word + ' '
    return to_query.split(' '), original_query

def rank_file(global_index, doc_index, query, num_docs):
    rank = 0
    for word in query:
        global_count = global_index.get(word, 0)
        if global_count == 0:
            idf = 0
        else:
            idf = math.log2(num_docs/global_count)
        freq = doc_index.get(word, 0)
        max_freq = max(doc_index.values())
        tf = freq/max_freq
        rank += idf * tf
    return rank

class rank_holder:
    def __init__(self):
        self.file = ""
        self.rank = 0

    def set_file(self, file):
        self.file = file

    def set_rank(self, rank):
        self.rank = rank

    def get_rank(self):
        return self.rank

    def get_file(self):
        return self.file

def query_run(to_query):
    #result_file = 'results.txt'
    query, original_query = get_query(to_query)
    query = stem_query(query)
    global_index, doc_indices = unpickle()
    file_list = glob.glob('To_be_posted/*.txt')
    rank_list = list()
    rank_dict = {}
    for file in file_list:
        rank = rank_file(global_index, doc_indices[file], query, len(file_list))
        temp = rank_holder()
        temp.set_file(file)
        temp.set_rank(rank)
        rank_list.append(temp)


    sorted_ranked = sorted(rank_list, key= rank_holder.get_rank, reverse=True)

    #outfile =  open(result_file, 'a')
    #outfile.write('query: ' + original_query + '\n')

    best_5 = sorted_ranked[:5]
    return best_5, doc_indices


    #print(sorted_ranked)

#query_run()