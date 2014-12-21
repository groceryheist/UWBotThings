#stream currently trending topics

import botUtil,helloTwitter as ht
import tweepy
import json
from threading import Timer
from threading import Thread
import threading
import time,os,codecs,StringIO,io
import sys
sys.path.append('models/')
from sqlalchemy import func,and_
from ModelBase import HashTag, Status, SessionFactory
from Twitter_User import Twitter_User
from Bot import Bot
import populateHashTag

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
            try:
                cursor.copy_from(chunktoCopy,'status',null='None',columns=['sid','txt','status_reply_id','author_id','retweet_id','retweet_count','user_reply_id','rawjson','created_at','trend_name','trend_query','is_truncated','url','status_reply_id_holding','retweet_id_holding'])
                helper.commit()
            except Exception as e:
                print(str(e))
            finally:
                chunktoCopy.close()

    def commit_data(self):
        
            chunktoCopy = self.currentChunk
            self._changeCurrentChunk()        
            thread = threading.Thread(target=self.write_chunk,args=[chunktoCopy])
            thread.start()
            
            print 'chunk of statuses written'


    # def on_limit(self,track):
    #     print "limited!"
    #     return False
    def findStatusTopic(self,tweepyStatus):
        matches = [topic for topic in self.topics if topic.name in tweepyStatus.text]
        if(len(matches) > 0):
            return matches[0]

    def on_limit(self,track):
        print( 'limit!' + str(track))
        return

    def write_status(self,tweepyStatus):
        sesh = SessionFactory()

        statusObj = Status.StatusFromTweepy(tweepyStatus)
        #print('status recieved')
        hts = statusObj.hashtags()
        try:
            for ht in hts:
                if sesh.query(HashTag).\
                    filter(and_(HashTag.status == ht.status,HashTag.hashtag == ht.hashtag)).\
                    scalar() is None:
                    sesh.add(ht)
            if sesh.query(Twitter_User).\
                filter(Twitter_User.uid == statusObj.author_id).scalar() is None:
                sesh.add(Twitter_User.UserFromTweepy(tweepyStatus.user))
                sesh.flush()
        except Exception as e:
            print str(e)
        finally:
            sesh.add(statusObj)
            sesh.commit()
            sesh.close()
        
    def on_status(self,tweepyStatus):
      #  t = Thread(target=self.write_status, args=[tweepyStatus])
       # t.start()
        #parse the status and write to chunk file
        statusObj = botUtil.status(tweepyStatus)

        self.currentChunk.write(unicode(statusObj).replace(u'\\\"','\\\\\"') + u'\n')
        self.linesWritten += 1
        if self.linesWritten >= self.chunk_size:
            self.commit_data()


    def on_error(self,status):
        print (time.localtime())
        print (status)
        time.sleep(600)
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
        print 'error!' + str(status)



# class trending(object):

#     def availableGeos(self):
#         available = self.api.trends_available()
#         for result in available:
#             if(result['placeType']['name'] == 'Country' and result['name'] == 'United States' and result['country'] == 'United States'):
#                 print result['woeid']
#                 return result['woeid']

#     def getUnitedStatesWOEID(self):
#         return '23424977'


#     def __init__(self,botAlias):
#         with botUtil.botUtil() as helper:
#             self.api = ht.Bot(botAlias).api

#     def getTopics(self,woeid):
#         apiResult = self.api.trends_place(id=woeid)[0]
#         with botUtil.botUtil() as helper:
#             helper.WriteTrends(apiResult)
#         return [botUtil.topic(trend) for trend in apiResult['trends']]


#     def streamTopics(self,topics,languages = None):        
#         stream = tweepy.Stream(self.api.auth,writeOutStatusListener(topics,self.api))
#         track = [t.name for t in topics]
#         print track
#         stream.filter(track=track, languages=languages, async=True)

class BigStream(object):
    def flatten(l):
        return [item for sublist in l for item in sublist]

    def refreshTopLists(self):
        sesh = SessionFactory()
        self.top5000users = [str(u.uid) for u in sesh.query(Twitter_User).\
            filter(Twitter_User.istarget == True).\
            order_by(Twitter_User.num_followers.desc())[0:5000]]

        s = sesh.query(HashTag.hashtag, func.count(HashTag.status)).\
            join(Status, Status.sid == HashTag.status).\
            join(Twitter_User, Status.author_id == Twitter_User.uid).\
            filter(Twitter_User.istarget == True).\
            group_by(HashTag.hashtag).all()
            
        self.top400Hts = [s[0] for s in sorted(s, key=lambda s: -s[1])[0:75]]
        sesh.close()


        
    def __init__(self):
        sesh = SessionFactory()
        bot = sesh.query(Bot).first()
        bot.wakeUp(sesh)
        print bot
        
        self.api = bot.api
       
        sesh.close()

    def run(self):
        while(True):
            t = Thread(target = self.reset)
            t.start()
            time.sleep(12*60*60)
            
        
    def reset(self):
        print('starting')
        if hasattr(self,'stream'):
            self.stream.disconnect()
            
        populateHashTag.run()
        self.refreshTopLists()
        self.stream = tweepy.Stream(self.api.auth, writeOutStatusListener([], self.api))
        self.stream.filter(follow=self.top5000users, track=self.top400Hts, languages=['en'], async=False)
        
if __name__ == '__main__':
    while(True):
        try:
            BigStream().run()
        except Exception as e:
            print str(e)
            time.sleep(600)
            
    
# print t.getTopicQueries(t.getUnitedStatesWOEID())

