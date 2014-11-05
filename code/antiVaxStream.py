import tweepy
import helloTwitter as ht, botUtil as bu
import time

import json

query = '#CDCwhistleblower'

# download every last #saynotovaccines 
#query once per 5 seconds
max_id = -1
has_results = True
max_count = 99999
while(has_results and max_count > 0):
	if(max_id < 0):
		current_page = ht.narrator.api.search(q=query,lang='en',count=100)
	else:
		current_page = ht.narrator.api.search(q=query,lang='en',count=100, max_id = max_id)

	max_count = max_count - 1
	has_results = len(current_page) != 0
	print len(current_page)
	max_id = min([item.id for item in current_page])
	# write results
	for status in current_page:
		bu.writeStatus(status)

	# print current_page
	time.sleep(5.001)