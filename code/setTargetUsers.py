# setTargetUsers.py
from sqlalchemy.orm.exc import NoResultFound
import io
import sys
sys.path.append("models/")
from ModelBase import SessionFactory
from Twitter_User import Twitter_User
from sqlalchemy import or_
import logging


class setTargetUsers(object):
    def parseparams(self, argv):
        pc = 0
        while(pc < len(argv)):
            param = argv[pc]
            if param == '-f':
                pc += 1
                self.filename = argv[pc]
            pc += 1

    def usage(self, argv):
        print "USAGE: python %s -f <userids file> -b <authenticated bot alias> -s [Optional] <starting with user id>"%(argv[0])

    def __init__(self, argv):
        self.parseparams(argv)

    def run(self, batchSize=1000):
        session = SessionFactory()

        count = 0
        print("running process")
       # first set all istargets to false
        for user in session.query(Twitter_User).filter(or_(
            Twitter_User.istarget, Twitter_User.istarget == None)):

            user.istarget = False
            count += 1
            if (count % batchSize) == 0:
                print("commit 1")
                session.commit()

        toChange = set([line.strip()
                        for line in io.open(self.filename).readlines()])
        for id in toChange:
            try:
                user = session.query(Twitter_User).filter(
                    Twitter_User.uid == id).one()
            except NoResultFound:
                logging.info('user id not found:%s' % id)

            user.istarget = True
        ## for user in session.query(Twitter_User).filter(
        ##         str(Twitter_User.uid) in toChange):
        ##     user.istarget = True
        ##     count += 1
        ##     if (count % batchSize) == 0:
        ##         session.commit()
        session.commit()

print("help")
setTargetUsers(sys.argv).run()
