UWBotThings
===========

The Patron Saint of inconsequential things


Known Dependencies:

tweepy, psycopgy2, nltk (must be version 2.* not 3.*. Use apt-get not pip)

Code Files: 
antiVaxStream.py - download all tweets for a query ever using search api into database
cleanCorpus.py - rules for cleaning tweet text before training models
HelloMarkov.py - generate tweets using nltk's language model
helloTwitter.py - authorize bots and play with the twitter api. 