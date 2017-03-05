from os import path #for wordcloud
from wordcloud import WordCloud
from PIL import Image #not needed????


def get_wordcloud(words): #takes a list of word-frequency pairs stored in tuples as input

    #mask = np.array(Image.open(path.join(d, "words.png")))


    f = open('static/words.txt', 'w+', encoding='utf-8')


    for t in words: #each word printed to the text file the same number of times as it appears in the tweets
        w = t[0]

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

    wordcloud = WordCloud(max_font_size=60).generate(text)

    #store image
    wordcloud.to_file("static/words.png")


