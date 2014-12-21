#HelloMarkov.py
import nltk
import psycopg2
import psycopg2.extras
import io
from nltk.probability import (ConditionalFreqDist,ConditionalProbDist,SimpleGoodTuringProbDist,LidstoneProbDist)
from nltk.tokenize import (BlanklineTokenizer,WhitespaceTokenizer)
from itertools import groupby
import re
import math
import botUtil

class randomTweetGenerator(object):

    def __init__(self,hashtag):
        self.corpusFile = hashtag + 'tweetCorpusClean.txt'
        self.makePlainTextCorpusFromDb(hashtag)
        mycorpus = nltk.corpus.PlaintextCorpusReader(root='.',fileids=self.corpusFile,word_tokenizer=WhitespaceTokenizer(),sent_tokenizer=BlanklineTokenizer())
            
        text = mycorpus.words()    
        self.lm = nltk.model.ngram.NgramModel(n = 3, train = text)
        
    def makePlainTextCorpusFromDb(self, hashtag = ''):
        connection = psycopg2.connect(database='SocialBots2', user='nate', password='b00mTown',host='alahele.ischool.uw.edu')
        cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor,name=hashtag+'builder')
        psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, cursor)

        cursor.execute("SELECT  DISTINCT txt, retweet_count FROM status WHERE status.txt ILIKE \'%%%s%%\' LIMIT 100000;"%hashtag)
        items = []
        for item in cursor.fetchall():
            n = int(math.ceil(math.log(item.retweet_count + 1, 10)))
            for i in range(n):
                items.append(item.txt)
        
        with io.open(self.corpusFile, mode='w', encoding='UTF-8') as f:
            f.writelines([ '{ { '+ txt + ' }' + '\n' for txt  in items])


    def nextWord(self,cfdist,w):
        return cfdist[w].max()    

    def generateTweet(self):
        startword = "{"
        isFound = False

        tries = 10
        while(not isFound and tries > 0):
            # print tries
            tries = tries - 1
            counts = {}
            cur = self.lm.generate(12,startword)
            isFound = True
            for key,group in groupby(sorted(cur), lambda x: x):
                if('#' in key):
                    if key in counts:
                        counts[key] = counts[key] + 1
                    else:
                        counts[key] = 1            
            result =  re.sub('&amp;','&',' '.join([ i.strip('{').strip('}') for i in cur]))
            if 'cdcwhistleblower' in result.lower() or len(result) > 140 or sum([1 for i in counts.itervalues() if i > 0]) > 3:
                isFound = False
        return result



    #for i in range(10):
     #   print generateTweet()

    # bigrams = nltk.bigrams(text)
    # trigrams = nltk.trigrams(text)

    # # pattern is 

    # cfd = nltk.ConditionalFreqDist(trigrams)

    # while(True):
    #     print nextWord(cfd,raw_input())


    #print mycorpus.sents(corpusFile)[0]

    # print ten tweets
    # for i in range(0, 9) :
        # latest = ' '.join(lm.generate(18,[""]))
        # print latest
        # print len(latest)
