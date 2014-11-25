import sys
sys.path.append("models/")
from Trend import Trend
from ModelBase import SessionFactory
import botUtil


with botUtil.botUtil() as bu:
    count = 0
    chunksize = 1000
    sesh = SessionFactory()
    allTrends = bu.listTrends(chunksize=chunksize)
    for record in allTrends:
        sesh.add(Trend.TrendFromOldRecord(record))
        count += 1
        if (count % chunksize) == 0:
            sesh.commit()
    sesh.commit()
    print count
