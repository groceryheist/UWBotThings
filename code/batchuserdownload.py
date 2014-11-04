#script to download user data to /db flat file

class batchuserdownload(object):

	def parseparams(argv):
		for arg in argv:

	def usage(argv):
		print "USAGE: python %s -f <userids file>"%(argv[0])