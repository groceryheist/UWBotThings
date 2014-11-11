#stream currently trending topics

import botUtil,helloTwitter as ht
import tweepy
import json
import threading
import time,os,codecs

class writeOutStatusListener(tweepy.StreamListener):

	def __init__(self,topics,api):
		self.linesWritten = 0	
		self.chunk_size = 3000
		self.lock = threading.Lock()
		self.topics = topics
		self.chunkFile0 = '~%sstreamChunk0'%id(self)
		self.chunkFile1 = '~%sstreamChunk1'%id(self)
		self.currentChunk = codecs.open(self.chunkFile0,mode='w',encoding='utf-8')
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
		self.currentChunk.close()		
		if(self.currentChunk == self.chunkFile0):
			self.currentChunk 	= codecs.open(self.chunkFile1, mode='w',encoding='utf-8')
		else:
			self.currentChunk = codecs.open(self.chunkFile0, mode='w',encoding='utf-8')

		self.linesWritten = 0
		self.lock.release()

	def commit_data(self):
		with botUtil.botUtil() as helper:
			chunktoCopy = self.currentChunk
			self._changeCurrentChunk()

			cursor = helper.GetUpdateCursor()
			chunktoCopy = open(chunktoCopy.name,mode='r')
			cursor.copy_from(chunktoCopy,'status')
			print 'chunk of statuses written'


	# def on_limit(self,track):
	# 	print "limited!"
	# 	return False

	def on_status(self,tweepyStatus):
	# parse the status and write to chunk file
		topic = [topic for topic in self.topics if topic.name in tweepyStatus.text][0:1]
		statusObj = botUtil.status(tweepyStatus,topic)
		self.currentChunk.write(statusObj.txt + '\n')
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


	def streamTopics(self,topics,language = None):		
		stream = tweepy.Stream(self.api.auth,writeOutStatusListener(topics,self.api))
		track = ','.join([t.name for t in topics])
		print track
		stream.filter(track=track, languages=language)

def flatten(l):
	return [item for sublist in l for item in sublist]

t = trending('testvaxBot')

topics = t.getTopics(t.getUnitedStatesWOEID())


t.streamTopics(topics[0:1])#,language = 'en')
# print t.getTopicQueries(t.getUnitedStatesWOEID())

