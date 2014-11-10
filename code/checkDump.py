#check all the users are in the db

import botUtil as helper
import io

with helper.botUtil() as bu:
	targets = bu.listUsers(targetOnly=True)
	cursor = bu.GetUpdateCursor()
	for user in targets:
		jobj = bu.parseJsonFromRecord(user)
		if(jobj):
			if('statuses_count' in jobj):
				numStatuses = jobj['statuses_count']
				bu.setStatusesCount(user.id,numStatuses,cursor)
	bu.commit()



