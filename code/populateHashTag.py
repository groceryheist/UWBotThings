#populate HashTag.py
import sys
sys.path.append("models/")
from ModelBase import Status, HashTag, SessionFactory
from sqlalchemy import and_, func, not_, update
import json

def column_windows(session, column, windowsize):
    """Return a series of WHERE clauses against 
    a given column that break it into windows.

    Result is an iterable of tuples, consisting of
    ((start, end), whereclause), where (start, end) are the ids.

    Requires a database that supports window functions, 
    i.e. Postgresql, SQL Server, Oracle.

    Enhance this yourself !  Add a "where" argument
    so that windows of just a subset of rows can
    be computed.

    """
    def int_for_range(start_id, end_id):
        if end_id:
            return and_(
                column>=start_id,
                column<end_id
            )
        else:
            return column>=start_id

    q = session.query(
                column, 
                func.row_number().\
                        over(order_by=column).\
                        label('rownum')
                ).\
                from_self(column)
    if windowsize > 1:
        q = q.filter("rownum %% %d=1" % windowsize)

    intervals = [id for id, in q]

    while intervals:
        start = intervals.pop(0)
        if intervals:
            end = intervals[0]
        else:
            end = None
        yield int_for_range(start, end)

def windowed_query(q, column, windowsize, limit = None, order_by_column = None):
    if(order_by_column is None):
        order_by_column = column
    """"Break a Query into windows on a given column."""
    count = 0
    for whereclause in column_windows(
                                        q.session, 
                                        column, windowsize):
        print str(q.filter(whereclause).order_by(order_by_column))
        if(limit is not None and count > limit):
            break
        for row in q.filter(whereclause).order_by(order_by_column):
            count += 1
            yield row
            if(limit is not None and count > limit):
                break
            

def run():
    offset = 0
    chunksize = 1000
    sesh = SessionFactory()
    sesh2 = SessionFactory()
    statuses = sesh.query(Status)#.filter(not_(Status.hashtagisset == True))
    count = 0

    for status in windowed_query(statuses, Status.sid, chunksize, limit=1000, order_by_column = Status.created_at.desc()):
        if(type(status.rawjson) == str or type(status.rawjson) == unicode):
            js = json.loads(status.rawjson)
        else:
            js = status.rawjson

        if('entities' in js):
            entities = js['entities']
            if 'hashtags' in entities:
                hts = entities['hashtags']
                for ht in hts:
                    sesh2.add(HashTag(status=status.sid, hashtag=ht['text']))
        count +=1


        sesh2.flush()
        if count % chunksize == 0:
            sesh2.commit()
    statuses.update({Status.hashtagisset: True})
    sesh.commit()
    sesh.close()
    sesh2.commit()
    sesh2.close()

if __name__ == '__main__':
    run()
