# botUtil.py
import psycopg2, psycopg2.extensions, psycopg2.extras
import tweepy
import json
import time

class botUtil(object):

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
		

	def parseCreatedAt(self,model):
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
		print rec
		return rec != 0		

	def writeUser(self,user_result,commit=True):
		
		uid = user_result.id
		name = user_result.screen_name
		user_id = self.tryGetAttribute(user_result,'user_id')
		created_at = self.parseCreatedAt(user_result)
		profile = self.tryGetAttribute(user_result,'description')


		cursor = self.connection.cursor(cursor_factory = psycopg2.extras.NamedTupleCursor)

		if not self.isUserInDb(uid):
			query = """ INSERT INTO twitter_user(id,user_name,profile,created_at,_json,user_id)
						VALUES(%s,%s,%s,%s,%s,%s);
					"""
			cursor.execute(query,(uid,name,profile,created_at,json.dumps(user_result._json),user_id))

			if commit:
				self.connection.commit()

			print 'wrote data for user %s'%(name)

	def writeStatusList(self,statusList):
		cursor = self.connection.cursor()

		for status in statusList:
			self.writeStatus(status,False,cursor)

		self.connection.commit()		

	def writeStatus(self,status,commit=True, cursor = None):
		
		if(cursor == None):
			cursor = self.connection.cursor()


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
		
		# query = """ INSERT INTO status(id,txt,reply_id,author_id,retweet_id,retweet_count,user_reply_id)
		# 	VALUES(%(sid)s,%(txt)s,%(reply_id)s,%(author_id)s,%(retweet_id)s,%(retweet_count)s,%(user_reply_id)s);
		# 	"""

		query = """ INSERT INTO status(id,txt,status_reply_id,author_id,retweet_id,retweet_count,user_reply_id,created_at,_json)
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);
			"""

		cursor.execute("""SELECT * FROM status WHERE id = """ + str(sid) + ";")
		if(cursor.rowcount == 0):
			# print status._json
		# _json = status._json
			cursor.execute(
				query,(sid,txt,reply_id,author_id,retweet_id,retweet_count,user_reply_id,created_at,json.dumps(status._json)))

			if(commit):
				self.connection.commit()

	def __init__(self):	
		self.connection = psycopg2.connect(database='SocialBots', user='postgres', password='postgres',host='localhost')

	def __exit__(self,type,value,traceback):
		self.connection.close()

	def __enter__(self):
		return self
