from os import path #for wordcloud
from wordcloud import WordCloud
from PIL import Image #not needed????


#import matplotlib.pyplot as plt #for plotting, not needed???


def get_wordcloud(words): #takes a list of word-frequency pairs stored in tuples as input

    #mask = np.array(Image.open(path.join(d, "words.png")))


    f = open('static/words.txt', 'w+', encoding='utf-8')


    for t in words: #each word printed to the text file the same number of times as it appears in the tweets
        w = t[0]
        #isascii = lambda w: len(w) == len(w.encode('ascii'))  #Only ascii strings can be plotted by wordcloud, so anything else is removed

        try:
            w.encode('ascii')
        except UnicodeEncodeError:
            isascii = False
        else:
            isascii = True
        
        if isascii:
            for i in range(t[1]):
                f.write(str(w) + ' ')
            
    f.close()
            
    #read the whole text.
    text = open('static/words.txt').read()

    #wordcloud = WordCloud(max_words=1000, mask=mask, stopwords=stopwords, margin=10,random_state=1).generate(text)
    wordcloud = WordCloud(max_font_size=60).generate(text)

    #store image
    wordcloud.to_file("static/words.png")


