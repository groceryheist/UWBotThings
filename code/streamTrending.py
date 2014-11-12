#stream currently trending topics

import botUtil,helloTwitter as ht
import tweepy
import json
import threading
import time,os,codecs,StringIO,io

class writeOutStatusListener(tweepy.StreamListener):

	def __init__(self,topics,api):
		self.linesWritten = 0	
		self.chunk_size = 1000
		self.lock = threading.Lock()
		self.topics = topics
		self.currentChunk = StringIO.StringIO()
		self.api = api

	def on_data(self, raw_data):
		"""Called when raw data is received from connection.
		Override this method if you wish to manually handle
		the stream data. Return False to stop stream and close connection.
		"""
		data = json.loads(raw_data)

		if 'in_reply_to_status_id' in data:
			status = tweepy.Status.parse(self.api, data)
			if self.on_status(status) is False:
				return False
		elif 'delete' in data:
			delete = data['delete']['status']
			if self.on_delete(delete['id'], delete['user_id']) is False:
				return False
		elif 'event' in data:
			status = tweepy.Status.parse(self.api, data)
			if self.on_event(status) is False:
				return False
		elif 'direct_message' in data:
			status = tweepy.Status.parse(self.api, data)
			if self.on_direct_message(status) is False:
				return False
		elif 'limit' in data:
			if self.on_limit(data['limit']['track']) is False:
				return False
		elif 'disconnect' in data:
			if self.on_disconnect(data['disconnect']) is False:
				return False
		elif 'warning' in data:
			if self.on_warning(data) is False:
				return False

		else:
			logging.error("Unknown message type: " + str(raw_data))


	def on_warning(self,data):
		print('falling behind')
		return False

	def _changeCurrentChunk(self):
		self.lock.acquire()
		self.currentChunk = StringIO.StringIO()		
		self.linesWritten = 0
		self.lock.release()

	def write_chunk(self,chunktoCopy):
		with botUtil.botUtil() as helper:
			cursor = helper.GetUpdateCursor()
			chunktoCopy.seek(0)
			cursor.copy_from(chunktoCopy,'status',null='None',columns=['id','txt','status_reply_id','author_id','retweet_id','retweet_count','user_reply_id','rawjson','created_at','trend_name','trend_query'])
			helper.commit()
			chunktoCopy.close()

	def commit_data(self):
		
			chunktoCopy = self.currentChunk
			self._changeCurrentChunk()		
			thread = threading.Thread(target=self.write_chunk,args=[chunktoCopy])
			thread.start()
			
			print 'chunk of statuses written'


	# def on_limit(self,track):
	# 	print "limited!"
	# 	return False
	def findStatusTopic(self,tweepyStatus):
		matches = [topic for topic in self.topics if topic.name in tweepyStatus.text]
		if(len(matches) > 0):
			return matches[0]

	def on_limit(self,track):
		print(track)
		return

	def on_status(self,tweepyStatus):
	# parse the status and write to chunk file
		topic = self.findStatusTopic(tweepyStatus)
		statusObj = botUtil.status(tweepyStatus,topic)
		self.currentChunk.write(unicode(statusObj).replace(u'\\\"','\\\\\"') + u'\n')
		self.linesWritten += 1
		if self.linesWritten >= self.chunk_size:
			self.commit_data()

	def on_error(self,status):
		print (time.localtime())
		print (status)
		return False

	def on_disconnect(self,notice):
		commit_data()
		os.remove(self.chunkFile0)
		os.remove(self.chunkFile1)


class StdOutListener(tweepy.StreamListener):
	def on_data(self,data):
		print data
		return True

	def on_error(self,status):
		print status



class trending(object):

	def availableGeos(self):
		available = self.api.trends_available()
		for result in available:
			if(result['placeType']['name'] == 'Country' and result['name'] == 'United States' and result['country'] == 'United States'):
				print result['woeid']
				return result['woeid']

	def getUnitedStatesWOEID(self):
		return '23424977'


	def __init__(self,botAlias):
		with botUtil.botUtil() as helper:
			self.api = ht.Bot(botAlias).api

	def getTopics(self,woeid):
		apiResult = self.api.trends_place(id=woeid)[0]
		with botUtil.botUtil() as helper:
			helper.WriteTrends(apiResult)
		return [botUtil.topic(trend) for trend in apiResult['trends']]


	def streamTopics(self,topics,languages = None):		
		stream = tweepy.Stream(self.api.auth,writeOutStatusListener(topics,self.api))
		track = [t.name for t in topics]
		print track
		stream.filter(track=track, languages=languages)

def flatten(l):
	return [item for sublist in l for item in sublist]

t = trending('testvaxBot')

topics = t.getTopics(t.getUnitedStatesWOEID())


t.streamTopics(topics,languages = ['en'])
# print t.getTopicQueries(t.getUnitedStatesWOEID())

