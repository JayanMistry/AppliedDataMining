#!/usr/bin/env python3

# Collection of functions from Feature extraction notebook.

import ftfy
import re
import regex
import grapheme

from collections import Counter

from math import log

import nltk
from nltk.corpus import stopwords

from wordcloud import WordCloud
import matplotlib.pyplot as plt

from os import listdir
from os.path import isfile, join, splitext, split

nltk.download('punkt')
nltk.download('maxent_treebank_pos_tagger')
nltk.download('stopwords')

hashtag_re = re.compile(r"#\w+")
mention_re = re.compile(r"@\w+")
url_re = re.compile(r"(?:https?://)?(?:[-\w]+\.)+[a-zA-Z]{2,9}[-\w/#~:;.?+=&%@~]*")
char_regex = regex.compile(r'\X')


def preprocess(text):
    p_text = hashtag_re.sub("[hashtag]",text)
    p_text = mention_re.sub("[mention]",p_text)
    p_text = url_re.sub("[url]",p_text)
    p_text = ftfy.fix_text(p_text)
    return p_text

def preprocess_remove(text):
    r_text = hashtag_re.sub("",text)
    r_text = mention_re.sub("",r_text)
    r_text = url_re.sub("",r_text)
    r_text = ftfy.fix_text(r_text)
    return r_text

tokenise_re = re.compile(r"(\[[^\]]+\]|[-'\w]+|[^\s\w\[']+)") #([]|words|other non-space)
def custom_tokenise(text):
    return tokenise_re.findall(text)

def print_tokens(tokens):
    for token in tokens: #iterate tokens and print one per line.
        print(token)
    print(f"Total: {len(tokens)} tokens")

def save_tokens(tokens, outfile):
    with open(outfile, 'w', encoding="utf-8") as f:
        for token in tokens: #iterate tokens and output to file.
            f.write(token + '\n')
        f.write(f"Total: {len(tokens)} tokens")

def read_list(file):
    with open(file) as f:
        items = []
        lines = f.readlines()
        for line in lines:
            items.append(line.strip())
    return items

def filter_fql(fql, predefined_list):
    return Counter({t: fql[t] for t in predefined_list}) #dict comprehension, t: fql[t] is token: freq.

def remove_list(fql, to_remove):
    filtered = Counter(fql)
    for r in to_remove:
        filtered.pop(r,None)
    return filtered

def ngrams(tokens, n, sep = "_", buffer="^"):
    buffered = [buffer] * (n-1) + tokens + [buffer] * (n-1) #add buffer either side to denote start and end
    return [sep.join(buffered[i:i+n]) for i in range(len(buffered)-n+1)] #list comprehension creating merged string of n chars, with a window of n through string

def merge_fqls(docs):
    merged = Counter()
    for doc in docs:
        merged += doc.tokens_fql
    return merged


def create_wordcloud(words):
    wordcloud = WordCloud().generate_from_frequencies(words)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()


def relative_freqs(fql):
    size = sum(fql.values())
    return {term: fql[term]/size for term in fql}

#Calculates log ratio for terms in corpus1, compared to corpus2.
#we pass the corpus sizes for ease.
#If the term is not present in corpus2, we make the frequency 0.5.
def log_ratio(corpus1, corpus1_size, corpus2, corpus2_size):
    return {term: log((corpus1[term]/corpus1_size)/((corpus2[term] if corpus2[term] else 0.5)/corpus2_size),2) for term in corpus1}


#doc is a Counter representing an fql from a document.
def tf(term, doc):
    return doc[term] / sum(doc.values()) #term freq / total terms (relative term freq)

def num_containing(term, corpus):
    return sum(1 for doc in corpus if term in doc) #counts docs in corpus containing term.

#1 added to numerator and denominator is for preventing division by zero. Equivalent of an extra document containing all terms once.
def idf(term, corpus):
    n_t = num_containing(term,corpus)
    return log((len(corpus)+1) / ((n_t) + 1))

def tfidf(term, doc, corpus):
    return tf(term, doc) * idf(term, corpus)



def import_party_folder(party):
    folder = "mps/" + party
    textfiles = [join(folder, f) for f in listdir(folder) if isfile(join(folder, f)) and f.endswith(".txt")]
    for tf in textfiles:
        username = splitext(split(tf)[1])[0] #extract just username from filename.
        print("Processing " + username)
        doc = Document({'username': username, 'party': party}) #include metadata
        with open(tf) as f:
            tweets = f.readlines()
        doc.extract_features(tweets)
        yield doc




class Document:
    def __init__(self, meta={}):
        self.meta = meta
        self.tokens_fql = Counter() #empty counter, ready to be added to with Counter.update.

    def extract_features(self, texts): #document should be iterable text lines, e.g. read in from file.
        for text in texts:
            p_text = preprocess(text)
            tokens = custom_tokenise(p_text.lower())
            self.tokens_fql.update(tokens) #updating Counter counts items in list, adding to existing Counter items.
