#stream currently trending topics

import botUtil,helloTwitter as ht
import tweepy
import json
import threading

class writeOutStatusListener(tweepy.StreamListener):

	def __init__(self,topics,api):
		self.linesWritten = 0	
		self.chunk_size = 3000
		self.lock = threading.Lock()
		self.topics = topics
		self.chunkFile0 = '~%sstreamChunk0',id(self)
		self.chunkFile1 = '~%sstreamChunk1',id(self)
		self.currentChunk = self.chunkFile0
		self.api = api

	def on_data(self,data):
		# copy lines to db and change file to write to
		if self.linesWritten >= self.chunk_size:
			self.lock.aquire()
			with botUtil() as helper:
				self.chunktoCopy = self.currentChunk
				if(self.currentChunk == self.chunkFile0):
					self.currentChunk = self.chunkFile1
				else:
					self.currentChunk = self.chunkFile0
				self.lock.release()

				cursor = helper.GetUpdateCursor()
				cursor.copy_from(self.chunktoCopy,'status')

		tweepyStatus = tweepy.Status(self.api).parse(self.api,json.loads(data))

		# parse the status and write to chunk file
		if(hasattr(tweepyStatus,'text')):
			topic = [topic for topic in self.topics if topic.name in tweepyStatus.text][0:1]
			statusObj = botUtil.status(tweepyStatus,topic)
			print statusObj.txt




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


	def streamTopics(self,topics,location,language):		

		stream = tweepy.Stream(self.api.auth,writeOutStatusListener(topics,self.api))
		stream.filter(track=','.join([t.query for t in topics]),locations = location, languages=language)

def flatten(l):
	return [item for sublist in l for item in sublist]

t = trending('testvaxBot')

uscoordinates = [[[-179.231086, 17.623468], [-179.231086, 71.434357], [179.859685, 71.434357], [179.859685, 17.623468], [-179.231086, 17.623468]]]
# uscoordinates = t.api.geo_search(query='usa',granularity='country')[0].bounding_box
location = ','.join(str(item) for item in flatten(flatten(uscoordinates)))
topics = t.getTopics(t.getUnitedStatesWOEID())
# print topics

t.streamTopics(topics[0:1],location,language = 'en')
# print t.getTopicQueries(t.getUnitedStatesWOEID())

