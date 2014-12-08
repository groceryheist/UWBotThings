# botUtil.py
import psycopg2, psycopg2.extensions, psycopg2.extras
import tweepy
import json
import time
import dateutil.parser
import sqlalchemy
import sys
sys.path.append("models/")
from ModelBase import SessionFactory


class topic(object):
    
    def __init__(self,topic_json):
        self.query = topic_json['query']
        self.name = topic_json['name']

    def __str__(self):
        return '{query=%s,name=%s}'%(self.query,self.name)

class status(object):
    def __init__(self,tweepyStatus,trendingTopic = None):
        self.sid = tweepyStatus.id
        self.txt = tweepyStatus.text
        self.reply_id = tweepyStatus.in_reply_to_status_id
        self.author_id = tweepyStatus.author.id

        self.created_at = botUtil.parseCreatedAt(tweepyStatus)
        if hasattr(tweepyStatus,'retweeted_tweepyStatus'):
            self.retweet_id = tweepyStatus.retweeted_tweepyStatus.id
        else:
            self.retweet_id = None

        self.retweet_count = tweepyStatus.retweet_count
        self.user_reply_id = tweepyStatus.in_reply_to_user_id
        self.topic = trendingTopic
        self.json = json.dumps(tweepyStatus._json)

    def getRecord(self,rawFormat = True):
        if(self.topic != None):
            topicName = self.topic.name
            topicQuery = self.topic.query
        else:
            topicName = ''
            topicQuery = ''
        if(rawFormat):
            return (self.sid,
                self.txt.replace('\n',' ').replace('\r',' '),
                None,
                None,
                self.retweet_id,
                self.retweet_count,
                self.user_reply_id,
                self.json.replace('\\','\\\\'),
                str(self.created_at).split('::')[0],
                topicName,
                topicQuery,
                None,
                None,
                self.reply_id,
                self.author_id
                    )
        else:
            return (self.sid,
                self.txt,
                None,
                None,
                self.retweet_id,
                self.retweet_count,
                self.user_reply_id,
                self.json,
                self.created_at,
                topicName,
                topicQuery,
                None,
                None,
                self.reply_id,
                self.author_id)

    def __unicode__(self):        
        return '\t'.join(unicode(item) for item in self.getRecord())


class botUtil(object):


    @staticmethod
    def parseStatus(self,status):
        sid = status.id
        txt = status.text
        reply_id = status.in_reply_to_status_id
        author_id = status.author.id

        created_at = self.parseCreatedAt(status)
        if hasattr(status,'retweeted_status'):
            retweet_id = status.retweeted_status.id
        else:
            retweet_id = None

        retweet_count = status.retweet_count
        user_reply_id = status.in_reply_to_user_id
        return (sid,txt,reply_id,author_id,retweet_id,retweet_count,user_reply_id,json.dumps(status._json),created_at)

    def getOldestUsersTweet(self,id):
        cursor = self.connection.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)
        query = """SELECT * FROM status WHERE author_id = %s ORDER BY id ASC LIMIT 1;"""
        params = (id)
        cursor.execute(query%params)
        oldest = cursor.fetchone()
        return oldest


    def trendIsStored(self,trend):
        cursor = self.connection.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)
        # primary key in this table is <trend_name,query>
        query = """SELECT COUNT(*) AS cnt FROM trends WHERE trend_name = %s AND query = %s;"""
        params = (trend['name'],trend['query'])
        cursor.execute(query,params)
        result = cursor.fetchone()
        cursor.close()
        return result.cnt == 1

    def writeTrend(self,cursor,trend,created_at):#as_of,cursor):
        if(self.trendIsStored(trend)):
            return True
        else:
            query = """INSERT INTO trends(trend_name,query,created_at) VALUES(%s,%s,%s);"""
            params = (trend['name'],trend['query'],created_at)#,as_of)
            cursor.execute(query,params)


    def WriteTrends(self,trends):
        cursor = self.GetUpdateCursor()
        for trend in trends['trends']:
            self.writeTrend(cursor,trend, psycopg2.extensions.TimestampFromPy(dateutil.parser.parse(trends['created_at'])))#,psycopg2.extensions.TimestampFromPy(trends['as_of']))
        self.commit()

    def GetUpdateCursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def ResultIter(self,cursor,chunksize = 1000):
        while True:
            results = cursor.fetchmany(chunksize)
            if not results:
                break
            for result in results:
                yield result                

    def parseJsonFromRecord(self,record):
        blob = record.rawjson
        if(blob):            
            obj = json.loads(blob)            
            return obj

    def getUser(self,id,cursor):
        query="""SELECT * FROM twitter_user WHERE id = %s""";
        params = (id)
        cursor.execute(query%params)
        return cursor.fetchone()



    def updateUser(self,id,field,value,cursor):
        query = """UPDATE twitter_user SET %s = %s WHERE id = %s""";
        params = (field,value,id)        
        cursor.execute(query%params) 
        print query%params

    def setStatusesCount(self,id,value,cursor):
        self.updateUser(id,'statuses_count',value,cursor)

    def setFollowerCount(self,id,follower_count,cursor):
        self.updateUser(id,'num_followers',follower_count,cursor)
        
    # def getStatusTextByTrend(self,trend):
    #     query = """SELECT * FROM 

    def setIsTarget(self,id,cursor,condition):
        query = """UPDATE twitter_user SET isTarget = %s WHERE id = %s;"""
        params = (condition,id)
        cursor.execute(query,params)
        print query%params


    def listUsers(self,targetOnly = False,chunksize=1000):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        if targetOnly:
            query = """SELECT * FROM twitter_user WHERE istarget = TRUE;"""
        else:
            query = """SELECT * FROM twitter_user;"""
        cursor.execute(query)
        return self.ResultIter(cursor,chunksize)

    def listTrends(self,chunksize=1000):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        query = "SELECT * FROM trends;"
        cursor.execute(query)
        return self.ResultIter(cursor, chunksize)

    def listStatuses(self,chunksize=1000,ignoreTrends=False):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor,name='mycursor')
        query = "SELECT * FROM status"
        if(ignoreTrends):
            query += " WHERE trend_name IS NULL"
        cursor.execute(query)
        return cursor
            
    def usersTweetsAreDown(self,uid, maxTweets = 3247):
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        query = "SELECT COUNT(*) AS cnt FROM status WHERE author_id = %s;"%uid


        # params = (uid)
        # cursor.execute(query,params)
        cursor.execute(query)
        # print query%params
        tweetsDown = cursor.fetchone().cnt
        statuses_count = self.getUser(uid, cursor).statuses_count
        return tweetsDown > maxTweets or tweetsDown >= statuses_count 



    def addFollowers(self,user,followers,api):

        queryTemplate = """INSERT INTO follows VALUES(%s,%s);"""
        if(self.isUserInDb(user)):
            print 'found user %s in db'%user
            cursor = self.connection.cursor() 
            for follow in followers:
                if(not self.isUserInDb(follow.id)):
                    self.writeUser(follow, commit=False)
                                        
                if not self.isFollowInDB(user,follow.id):
                    print 'user %s follows user %s'%(user,follow.id)
                    cursor.execute(queryTemplate,(user,follow.id))
                else:
                    return False
        else:
            self.fetchAndInsertUser(user,api)

        self.connection.commit()
        return True


    def fetchAndInsertUser(self,follow,api):
        print 'fetching user %s'%follow
        time.sleep(5.1)
        user = api.get_user(follow)
        self.writeUser(user, commit = False)
        
    @staticmethod
    def parseCreatedAt(model):
        if(hasattr(model,'created_at')):
            created_at = psycopg2.extensions.TimestampFromPy(model.created_at)
        else:
            created_at = None
        return created_at

    def tryGetAttribute(self,model,attribute):
        if(hasattr(model,attribute)):
            return getattr(model,attribute)
        else:
            return None


    def isFollowInDB(self, user, follow):
        cursor = self.connection.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)        

        cursor.execute("""SELECT COUNT(*) AS cnt FROM follows WHERE follower_id = %s AND followed_id = %s;""",(user,follow))
        rec = cursor.fetchone().cnt
        return rec == 1


    def isUserInDb(self,uid):
        cursor = self.connection.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)

        cursor.execute("""SELECT COUNT(*) AS cnt FROM twitter_user WHERE id = """ + str(uid) + ';')
        rec = cursor.fetchone().cnt
        # print rec
        return rec != 0        

    def writeUser(self,user_result,commit=True):
        tweepy.User
        uid = user_result.id
        name = user_result.screen_name
        user_id = self.tryGetAttribute(user_result,'user_id')
        created_at = self.parseCreatedAt(user_result)
        profile = self.tryGetAttribute(user_result,'description')

        cursor = self.connection.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)

        if not self.isUserInDb(uid):
            query = """ INSERT INTO twitter_user(id,user_name,profile,created_at,rawjson,user_id)
                        VALUES(%s,%s,%s,%s,%s,%s);
                    """
            
            cursor.execute(query,(uid,name,profile,created_at,json.dumps(user_result._json),user_id))

            if commit:
                self.connection.commit()

            print 'wrote data for user %s'%(name)

    def isStatusInDb(self,sid):
        cursor = self.connection.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)

        query = """SELECT COUNT(*) AS cnt FROM status WHERE id = """ + str(sid) + ";"
        cursor.execute(query)
        result = cursor.fetchone()
        return result.cnt >= 1


    def writeStatusList(self,statusList):
        cursor = self.connection.cursor()

        for status in statusList:
            self.writeStatus(status,False,cursor)

        self.connection.commit()        


    def writeStatus(self,tweepyStatus,commit=True, cursor = None):
        
        if(cursor == None):
            cursor = self.connection.cursor()
    
        # query = """ INSERT INTO tweepyStatus(id,txt,reply_id,author_id,retweet_id,retweet_count,user_reply_id)
        #     VALUES(%(sid)s,%(txt)s,%(reply_id)s,%(author_id)s,%(retweet_id)s,%(retweet_count)s,%(user_reply_id)s);
        #     """
        statusObj = status(tweepyStatus = tweepyStatus)
        params = statusObj.getRecord(False)

        query = """ INSERT INTO status(id,txt,status_reply_id,author_id,retweet_id,retweet_count,user_reply_id,rawjson,created_at,trend_name,trend_query)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
            """

        # cursor.execute("""SELECT * FROM status WHERE id = """ + str(sid) + ";")
        # if(cursor.rowcount == 0):
        if not self.isStatusInDb(statusObj.sid):
            cursor.execute(query,params)

            if(commit):
                self.connection.commit()




    def __init__(self):    
        self.connection = psycopg2.connect(database='SocialBots2', user='nate', password='b00mTown',host='alahele.ischool.uw.edu')

    def __exit__(self,type,value,traceback):
        self.connection.commit()
        self.connection.close()

    def __enter__(self):
        return self
















