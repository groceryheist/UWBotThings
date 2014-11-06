#Download users followers and followees
import helloTwitter as ht, botUtil as bu
import tweepy
import sys,io,time

class getFollowers(object):
	consumer_key = 'BefDhm8Lfs1jBrS22JRsZER44'
	consumer_secret = 'eAg2miijN0hFy1r9e5oCHGzc10qw2NTozQLAacGEZS5jYYt8bF'

	def parseparams(self,argv):
		pc = 0
		while(pc < len(argv)):
			param = argv[pc]
			if param == '-f':
				pc += 1
				self.filename = argv[pc]
			if param == '-b':
				pc += 1
				self.bot = ht.Bot(argv[pc])
			pc += 1

	def usage(self,argv):
		print "USAGE: python %s -f <userids file> -b <authenticated bot alias>"%(argv[0])

	def __init__(self,argv):
		try:
			self.parseparams(argv)
			self.filename
			self.bot
		except Exception:
			self.usage(argv)

	def run(self, startingwith = None):
		started = startingwith == None
		with bu.botUtil() as helper:
			with io.open(self.filename) as fs:
				for line in fs.readlines():
					if not started:
						if line.strip() == startingwith:
							print 'started'
							started = True

					if started:	
						page = -1
						try:
							followers,cursors = self.bot.api.followers(id=line, cursor=page)
							print cursors
							while len(followers) > 0:
								
								print 'found followers for %s'%line
								helper.addFollowers(line, followers, self.bot.api)										
								time.sleep(60)		
								followers,cursors = self.bot.api.followers(id = line,cursor = cursors[1])

						except Exception as e:
							print 'fetching followers for %s'%line
							print e
							time.sleep(5.1)

						except tweepy.TweepError as e:
							print 'fetching followers for %s'%line
							print e
							if str(e.reason) == "[{'message': 'Rate limit exceeded', 'code': 88}]":
								time.sleep(15*60)

getFollowers(sys.argv).run(startingwith = "15235948")