from flask import Flask, render_template, request, redirect, json
import json
import preprocessing #regex and tweet tokenising module
import visualisation #graphically displaying data

import operator
from collections import Counter
from datetime import datetime, timedelta
import urllib #for url encoding strings
from application_only_auth import Client #for authentication with and making queries to twitter api
from nltk import bigrams #might be useful later
import nltk.collocations # not needed?
from nltk.util import ngrams
from collections import defaultdict
import operator

app = Flask(__name__)


@app.route("/")

def main():
    return render_template('index.html')

@app.route("/handlesearch")

def handlesearch():
    return render_template('handlesearch.html')

@app.route("/hashtagsearch")

def hashtagsearch():
    return render_template('hashtagsearch.html')

@app.route("/handle", methods = ['POST'])
def handle():
    handle=request.values.get('handle')
  
    CONSUMER_KEY='B6bmv9Pnpw728Ub3ZZyKbUHLK'
    CONSUMER_SECRET='OmUVg3oBvaAfocVecDXt7ydyr2IvWA6dneCY2LQEPuiCSmztHS'
    client = Client(CONSUMER_KEY, CONSUMER_SECRET)
    token = client._get_access_token()

    url = 'https://api.twitter.com/1.1/search/tweets.json?q=' + '@' + handle + '&count=100'
    tweets = client.request(url) #a dictionary
    statuses = tweets["statuses"] #a list of dictionaries where each is a tweet o_o
    tweets_list = [] #retrieve text of each tweet and compile into list
    for tweet in statuses:
        tweets_list.append(tweet["text"])
            
    
    return render_template('handle.html',statuses=statuses, tweets_list=tweets_list)
    
    
    

@app.route("/hashtag", methods=['POST', 'GET'])

def hashtag():
    hashtag1=request.values.get('hashtag1')
    hashtag2=request.values.get('hashtag2')
    result_type=request.values.get('result_type_select')
    safe_filter=request.values.get('safe_filter_checkbox')
    lang_restrict=request.values.get('lang_restrict_checkbox')
    exclude_retweets=request.values.get('exclude_retweets_checkbox')
    exclude_replies=request.values.get('exclude_replies_checkbox')
    until_value=int(request.values.get('until_select'))
    #looks for tweets up until this date
    until_date = datetime.today() - timedelta(days=until_value)
    until_date = until_date.strftime('%Y-%m-%d') #puts date in YYYY-MM-DD format as required by Twitter
    
    CONSUMER_KEY='B6bmv9Pnpw728Ub3ZZyKbUHLK'
    CONSUMER_SECRET='OmUVg3oBvaAfocVecDXt7ydyr2IvWA6dneCY2LQEPuiCSmztHS'


    #geo data
    geo_data = {
	"type": "FeatureCollection",
	"features": []
        }

    client = Client(CONSUMER_KEY, CONSUMER_SECRET)
    
    url_query = '#' + hashtag1 + (('+' + '#' + hashtag2) if hashtag2 != '' else '')
    token = client._get_access_token()
    if safe_filter:  #applying optional filters
        url_query += '+filter:safe' 
    if exclude_retweets:
        url_query += '+exclude:retweets'
    if exclude_replies:
        url_query += '+exclude:replies'

       
   #tweet mode set to extended to get full 140 character tweet plus extra links


        
    params_to_encode = {'count':100, 'q' : url_query, 'until':until_date, 'result_type':result_type, 'tweet_mode':'extended'} #parameters to be encoded in the url added to a dictionary
    if lang_restrict:
        params_to_encode['lang']='en'
    urlappend = urllib.parse.urlencode(params_to_encode, safe='') #urllib function encodes the parameters
    url = 'https://api.twitter.com/1.1/search/tweets.json?' + urlappend #full url
    
    tweets = client.request(url) #a dictionary
    statuses = tweets["statuses"] #a list of dictionaries where each is a tweet 

    tweets_list = [] #retrieve text of each tweet and compile into list
    count_non_twitter=Counter()
    count_stop=Counter()
    count_hash=Counter()
    count_user=Counter()
    count_all=Counter()
    bigrams_all=Counter()
    trigrams_all=Counter()
    bigrams_stop=Counter()
    trigrams_stop=Counter()

    raw_terms=[]
    stop_terms = []

    co_matrix = defaultdict(lambda : defaultdict(int)) #the co-occurrences matrix
     
    for tweet in statuses:
        tweets_list.append(tweet["full_text"])
        preprocessing.get_non_twitter_terms(tweet,count_non_twitter)
        preprocessing.get_stop_terms(tweet,count_stop) #finds tokens and adds them to counter
        preprocessing.get_hash_terms(tweet,count_hash)
        preprocessing.get_user_terms(tweet,count_user)
        preprocessing.get_all_terms(tweet,count_all)
        raw_terms += preprocessing.get_words_list(tweet)
        stop_terms += preprocessing.get_stopwords_list(tweet)#with stopwords removed

        terms_only = preprocessing.get_stopwords_list(tweet)
     
        #build co-occurrence matrix
        for i in range(len(terms_only)-1):            
            for j in range(i+1, len(terms_only)):
                w1, w2 = sorted([terms_only[i], terms_only[j]])                
                if w1 != w2:
                    co_matrix[w1][w2] += 1

        #get geo data
        if tweet["coordinates"]:
            geo_json_feature = {
                "type": "Feature",
                "geometry": tweet["coordinates"],
                "properties": {
                    "text": tweet["full_text"],
                    "created_at": tweet["created_at"]
                }
            }
            geo_data["features"].append(geo_json_feature)

    
    #save geo data
    with open('static/geo_data.json', 'w') as out_file:
        out_file.write(json.dumps(geo_data, indent=4))
    out_file.close()


    most_common = count_stop.most_common(20)
    most_common_non_twitter = count_non_twitter.most_common(20) #list of tuple pairs
    all_hashtags = count_hash.most_common(10)
    all_users = count_user.most_common(10)
    all_terms = count_all.most_common()

    preprocessing.get_ngrams_for_counter(raw_terms,bigrams_all,2)
    preprocessing.get_ngrams_for_counter(raw_terms,trigrams_all,3)
    preprocessing.get_ngrams_for_counter(stop_terms,bigrams_stop,2)
    preprocessing.get_ngrams_for_counter(stop_terms,trigrams_stop,3)

    visualisation.get_wordcloud(count_non_twitter.most_common(50))

    common_bigrams = [b for b in bigrams_stop.most_common() if b[1] >= 3]
    common_trigrams = [t for t in trigrams_stop.most_common() if t[1] >= 3 and t in trigrams_all.most_common()] #no rigrams will contain stopwords, but this also prevents a trigram from being formed if there are removed stopwords in between the words that form it
    bigrams_to_remove = []
 

    for b in common_bigrams:
        for t in common_trigrams:
            if b[0][0] and b[0][1] in t[0]:   
                bigrams_to_remove.append(b)
                

    common_bigrams = [b for b in common_bigrams if b not in bigrams_to_remove and b in bigrams_all.most_common()] #prevents two words with a removed stopwords in between from becoming a bigram



    co_matrix_max = []
    # For each term, looks the most common terms that co-occur within a tweet
    for t1 in co_matrix:
        t1_max_terms = sorted(co_matrix[t1].items(), key=operator.itemgetter(1), reverse=True)[:5]
        for t2, t2_count in t1_max_terms:
            co_matrix_max.append(((t1, t2), t2_count))
    # Get the most frequent co-occurrences
    co_terms_max = sorted(co_matrix_max, key=operator.itemgetter(1), reverse=True)[:5]




    return render_template('hashtag.html', tweets_list=tweets_list, all_hashtags=all_hashtags, all_users=all_users,
    most_common_non_twitter=most_common_non_twitter, common_bigrams=common_bigrams, common_trigrams=common_trigrams, co_terms_max=co_terms_max)
    
   


if __name__ == "__main__":
    context = ('cert.crt', 'cert.key') #self signed certificate
    app.run(host='0.0.0.0', port=443, ssl_context=context, threaded=True, debug=True)
