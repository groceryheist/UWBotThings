# download all tweets from a user
import helloTwitter as ht, botUtil as bu
import tweepy
import sys,io,time

class getTweets(object):
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
		self.parseparams(argv)

	def pullEntireTimeline(self,api,uid,botUtil):
		has_results = True
		max_id = -1
		while(has_results):
			if(max_id < 0):
				current_page = api.user_timeline(id=uid)
			else:
				current_page = api.user_timeline(id=uid, max_id = max_id)
			
			has_results = len(current_page) > 0
			if(has_results):
				max_id = min([item.id for item in current_page])
			print 'writing page of status for %s'%uid
			botUtil.writeStatusList(current_page)
			time.sleep(5.01)



	def run(self):
		with bu.botUtil() as helper:
			with io.open(self.filename) as fs:
				for line in fs.readlines():
					self.pullEntireTimeline(self.bot.api,line,helper)

getTweets(sys.argv).run()