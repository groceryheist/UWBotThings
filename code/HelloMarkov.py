#HelloMarkov.py
import nltk
import psycopg2
import psycopg2.extras
import io
from nltk.probability import (ConditionalFreqDist,ConditionalProbDist,SimpleGoodTuringProbDist,LidstoneProbDist)
from nltk.tokenize import (BlanklineTokenizer,WhitespaceTokenizer)
from itertools import groupby
import regex

corpusFile = '../data/tweetCorpusClean.txt'

def makePlainTextCorpusFromDb():
	connection = psycopg2.connect(database='SocialBots', user='postgres', password='postgres',host='localhost')
	cursor = connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
	psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, cursor)

	cursor.execute("SELECT txt FROM status;")

	with io.open('corpusFile', mode='w', encoding='UTF-8') as f:
		f.writelines([ '{ { '+ item.txt + ' }' + '\n' for item in cursor.fetchall()])


def nextWord(cfdist,w):
	return cfdist[w].max()



mycorpus = nltk.corpus.PlaintextCorpusReader(root='.',fileids=corpusFile,word_tokenizer=WhitespaceTokenizer(),sent_tokenizer=BlanklineTokenizer())
# est = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
# est = lambda fdist, bins: SimpleGoodTuringProbDist(fdist, None)

text = mycorpus.words()
# unigrams = nltk.words(text)

# simport nltk.model.ngram
lm = nltk.model.ngram.NgramModel(n = 3, train = text)
# , estimator = est) 
print lm
print lm._backoff
def generateTweet():
	startword = lm._backoff.generate(1,'{')
	isFound = False

	tries = 10
	while(not isFound and tries > 0):
		# print tries
		tries = tries - 1
		counts = {}
		cur = lm.generate(12,startword)
		isFound = True
		for key,group in groupby(sorted(cur), lambda x: x):
			if('#' in key):
				if key in counts:
					counts[key] = counts[key] + 1
				else:
					counts[key] = 1			

		if len(cur) > 140 or sum([1 for i in counts.itervalues() if i > 0]):
			isFound = False
	
	return re.sub('&amp;','&',' '.join([ i.strip('{').strip('}') for i in cur])).

# bigrams = nltk.bigrams(text)
# trigrams = nltk.trigrams(text)

# # pattern is 

# cfd = nltk.ConditionalFreqDist(trigrams)

# while(True):
# 	print nextWord(cfd,raw_input())


#print mycorpus.sents(corpusFile)[0]

# print ten tweets
# for i in range(0, 9) :
	# latest = ' '.join(lm.generate(18,[""]))
	# print latest
	# print len(latest)