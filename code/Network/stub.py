import sys
sys.path.append("../models/")

from ModelBase import Status, SessionFactory
import codecs

session = SessionFactory()
print unicode(session.query(Status)[0])
