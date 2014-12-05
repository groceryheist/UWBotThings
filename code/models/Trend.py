from ModelBase import Trend


class Trend(Trend):

    @staticmethod
    def TrendFromOldRecord(record):
        return Trend(trend_name=record.trend_name,
                     query=record.query,
                     created_at=record.created_at,
                     as_of=record.as_of
                     )

