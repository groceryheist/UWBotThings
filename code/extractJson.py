import botUtil
import sets

def assignTargetSet():
	targetSet = sets.ImmutableSet([line.strip() for line in open("../data/beta-randomized.txt").readlines()])

	with botUtil.botUtil() as bu:
		users = bu.listUsers()
		updateCursor = bu.GetUpdateCursor()
		# numQueries = 0
		for u in users:
			if(str(u.id) in targetSet):
				bu.setIsTarget(u.id,updateCursor,True)
			else:
				bu.setIsTarget(u.id,updateCursor,False)
		bu.commit()

def setFollowerCountFromJson():
	with botUtil.botUtil() as bu:
		users = bu.listUsers()
		updateCursor = bu.GetUpdateCursor()
		for u in users:
			obj = bu.parseJsonFromRecord(u)
			if(obj):
				if('followers_count' in obj):
					bu.setFollowerCount(u.id,obj['followers_count'],updateCursor)

		bu.commit()

setFollowerCountFromJson()