#
	#session
#	request.GET.get
import string
import tweepy
import psycopg2, psycopg2.extras

import time

consumer_key = 'BefDhm8Lfs1jBrS22JRsZER44'
consumer_secret = 'eAg2miijN0hFy1r9e5oCHGzc10qw2NTozQLAacGEZS5jYYt8bF'

# we are single threaded for now. 
# global connection is thread safe
conn = psycopg2.connect(database='SocialBots', user='postgres', password='postgres',host='localhost')

class MessageToLongException(Exception):
	def __init__(self,value):
		self.value = value
	def str():
		return self.value

class Bot:

	botKeysFile = '../data/AuthorizedBots.tsv'

	def __init__(self,alias,auth = None):
		self._me = None
		if(auth):
			self.auth = auth
			self.alias = alias
			self.api = tweepy.API(auth)
			self.isAuthorized = True
		else:
			self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
			self.alias = alias
			self.Authorize()		
			self.api = tweepy.API(self.auth)	
			self.isAuthorized = True
		

	def Authorize(self):
		self.isAuthorized = self.AuthorizeFromFile()		
		if(not self.isAuthorized):
			self.isAuthorized = self.AuthorizeBotAccount()

	def UserName(self):
		return self.auth.get_username()

	def me(self):
		if(not self._me):
			self._me = self.api.me()
		return self._me

	#TODO: use a bot database instead of flat file here if # of bots grows
	def AuthorizeFromFile(self):
		# try:
			cur = conn.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)
			cur.execute(str.format("SELECT user_id,access_key,access_secret,email,password,alias FROM bot WHERE alias = '{0}';",self.alias))
			if(cur.rowcount == 0):
				return False
			
			assert(cur.rowcount == 1)
			result = cur.fetchone()
			self.auth.set_access_token(result.access_key,result.access_secret)
			self.api = tweepy.API(self.auth)
			return True

		# except Exception:
		# 	print "Error reading authorization file!" 

	# def LatestStatus(self):
	def AuthorizeBotAccount(self):
		try:
			redirect_url = self.auth.get_authorization_url()
		except tweepy.TweepError:
			print 'Error! Failed to get request token'

		print self.alias + redirect_url
		code = raw_input()

		try:
			self.auth.get_access_token(code)			
			f = open(self.botKeysFile,'a')
			f.write(str.format("\n{0}\t{1}\t{2}",self.alias,self.auth.access_token.key,self.auth.access_token.secret))
			isAuthorized = True
			self.api = tweepy.API(self.auth)
		except tweepy.TweepError:
			print 'Error! Failed to get access token'

		cur = conn.cursor()
		user = self.me()
		
		cur.execute(str.format("INSERT INTO twitter_user(id,user_name) VALUES ({0},'{1}');",user.id,auth.get_username))

		cur.execute(str.format("INSERT INTO bot VALUES({0},'{1}','{2}','{3}','{4}','{5}');",
			user.id,
			self.auth.access_token.key,
			self.auth.access_token.secret,
			'',
			'',
			self.alias))


		conn.commit()

	def LatestStatus(self):
		try:
			timeline = self.api.user_timeline(count=1)
			if(len(timeline) > 0):
				return timeline[0]
		except TweepError:
			print 'Error! Failed to get user timeline'


class StreamListener(tweepy.StreamListener):
	def on_status(self, tweet):
		print repr("new status" + tweet.text)
	def on_exception(self,exception):
		print 'exception' + str(exception)
	def on_error(self,error):
		print 'error' + str(error)
	def on_disconnect(self,notice):
		print 'notice' + str(notice)

#access_token = '2842898476-5jnI5HjMQs4t0ZB1yMb6eZRixlejMJrs27PyP5D'
#access_token_secret = 'TIZVWnLjybdZYduXFai4CPHB2GrLGG5p4C0EmpYbOARq5'
access_token = '2838720400-1mqpL8Tg9ltuCqtsjLoXxAPep3PBg6AxkHZiarn'
access_token_secret = 'p6rvcJJIgAwKpPTIah396bHetIQmvd5cpKFqbnjbN0hlK'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# auth.set_access_token(access_token,access_token_secret)

# api = tweepy.API(auth)

#api.update_status("hello twitter")
#for result in tweepy.Cursor(api.search,q='#saynotovaccines',result_type='popular').items(20):
# 	print result.text
# l = StreamListener()

# franAuth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# franAuth.set_access_token('2868387492-zE74EVh8hGuCLThVz7XltMTNjtTbw9Gub4sOpUU','I9XC2iCgeGzdfnKLuD2ugeqpUfzQQBSMjDKWPgjCOsuFJ')


#narrator = Bot('narrator',auth)

# Bernardo = Bot('Bernardo,Officer')
# fransicso = Bot('fransicso, a soldier')

# testvaxBot = Bot('testvaxBot')
# import HelloMarkov,random

# #times in seconds
# def sleepRandom(min,max):
# 	dur = random.randint(min,max)
# 	print "sleeping for dur:" + str(dur)
# 	time.sleep(dur)


# def tweetNTimes(bot, printTweet = False):
# 	ntimes = random.randint(0,10)

# 	for i in range(0,ntimes):
# 		tweet = HelloMarkov.generateTweet()
# 		if(printTweet):
# 			print tweet

# 		bot.api.update_status(tweet)
# 		sleepRandom(60,420)


# # tweet according to a time patter
# while(True):
# 	tweetNTimes(testvaxBot, True)
# 	sleepRandom(60*60*0.75,60*60*1.5)


# fransicso.me().id
# narrator.me().id
# Bernardo.me().id

# print fransicso.api.create_friendship(id = Bernardo.me().id,follow=True)
# print Bernardo.api.create_friendship(id = fransicso.me().id,follow=True)
# print Bernardo.api.user_timeline(fransicso)
# print narrator.me()

# fransicso.api.update_status(status = '@'+ Bernardo.UserName() + ' Nay, answer me: stand, and unfold yourself.', in_reply_to_status_id= Bernardo.LatestStatus().id)
#tagListener = tweepy.Stream(api.search(q='#saynotovaccines',result_type='mixed'),l))
#tagListener = tweepy.Stream(auth,l)

#tagListener.filter(track=['#saynotovaccines'])



