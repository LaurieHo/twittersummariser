from nltk.tokenize import word_tokenize
import re
from nltk.corpus import stopwords
import string
import operator
from collections import Counter
from nltk import bigrams #not needed rn may be useful later
from nltk.util import ngrams


 

 
def nltk_preprocess(tweet, lowercase=False): #backup tokenizer, doesn't recognise #hashtags or @usernames
    tokens = word_tokenize(tweet)
    return tokens


 
emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
 
regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # usernames
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hashtags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # urls
 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - or '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # any other string
]
    
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)


punctuation = list(string.punctuation) #removes punctuation and unimportant words from tokens
unwanted_tokens = ['rt', 'via', '’', '”', '“', '...', '…', 'amp', 'lt', 'gt']
stop = stopwords.words('english') + punctuation + unwanted_tokens  #stopwords
 
def tokenize(t):
    return tokens_re.findall(t)
 
def preprocess(t, lowercase=True):

    tokens = tokenize(t)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens


def get_all_terms(t,counter):
    terms = [term for term in preprocess(t["full_text"])] #gets tokens from each tweet
    return counter.update(terms)

def get_hash_terms(t,counter):
    terms = [term for term in preprocess(t['full_text']) if term.startswith('#')]
    return counter.update(terms)

def get_user_terms(t,counter):
    terms = [term for term in preprocess(t['full_text']) if term.startswith('@')]
    return counter.update(terms)


def get_stop_terms(t,counter):
    terms = [term for term in preprocess(t['full_text']) if term not in stop]
    return counter.update(terms)

def get_non_twitter_terms(t,counter):
    terms = [term for term in preprocess(t['full_text']) if term not in stop and not term.startswith(('#', '@'))] 
    return counter.update(terms)

def get_stopwords_list(t): #similar to get_non_twitter_terms but returns list instead of updating counter
    terms = [term for term in preprocess(t["full_text"]) if term not in stop and not term.startswith(('#', '@'))]
    return terms

def get_words_list(t): #doesn't remove stopwords
    filter = punctuation + unwanted_tokens
    terms = [term for term in preprocess(t["full_text"]) if term not in filter and not term.startswith(('#', '@'))]
    return terms


def get_ngrams_for_counter(l,counter,n): #takes a list of words and a counter to update with the ngrams found
    return counter.update(ngrams(l, n))

    
    
 
