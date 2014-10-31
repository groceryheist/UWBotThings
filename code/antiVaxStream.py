import tweepy
import helloTwitter as ht
import time
import psycopg2
import psycopg2.extensions
import psycopg2.extras
import json

query = '#CDCwhistleblower'
connection = psycopg2.connect(database='SocialBots', user='postgres', password='postgres',host='localhost')
cursor = connection.cursor()


def writeStatus(status):
	sid = status.id
	txt = status.text
	reply_id = status.in_reply_to_status_id
	author_id = status.author.id

	if(hasattr(status,'created_at')):
		created_at = psycopg2.extensions.TimestampFromPy(status.created_at)
	else:
		created_at = None

	
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

		connection.commit()

# download every last #saynotovaccines 
#query once per 5 seconds
max_id = -1
has_results = True
tweepy.Status
max_count = 99999
while(has_results and max_count > 0):
	if(max_id < 0):
		current_page = ht.narrator.api.search(q=query,lang='en',count=100)
	else:
		current_page = ht.narrator.api.search(q=query,lang='en',count=100, max_id = max_id)

	max_count = max_count - 1
	has_results = len(current_page) != 0
	print len(current_page)
	max_id = min([page.id for page in current_page])
	# write results
	for status in current_page:
		writeStatus(status)

	# print current_page
	time.sleep(5.001)