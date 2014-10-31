#cleanCorpus.py
import urlparse

corpusFile = '../data/tweetCorpus.txt'
cleanFile = '../data/tweetCorpusClean.txt'

def cleanLine(line):
	# split by ' '
	split = line.split(' ')
	return ' '.join([token.strip('@') for token in split if not '@' in token and not token.lower() == 'rt' and not '//' in token])


def cleanCorpus(corpusFile):
	out = open(cleanFile,'w')
	out.writelines([cleanLine(line) for line in open(corpusFile,'r').readlines()])

cleanCorpus(corpusFile)
