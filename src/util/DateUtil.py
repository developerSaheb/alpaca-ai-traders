from datetime import timedelta, date
from datetime import date


class DateUtil(object):

    @staticmethod
    def date_range(start_date: date, end_date: date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    @staticmethod
    def days_between(d1, d2):
        return abs((d2 - d1).days)
