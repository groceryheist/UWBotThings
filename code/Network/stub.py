import sys
sys.path.append("../models/")
import ModelBase

session = ModelBase.SessionFactory.Session()
print(session.Query("Status")[0])