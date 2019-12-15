import datetime, random, string


class StringUtil(object):

    @staticmethod
    def ts_to_string(t):
        if t:
            return '{date:%Y-%m-%d %H:%M:%S}'.format( date=t)
        else:
            return ''

    @staticmethod
    def get_now_string():
        return '{date:%Y-%m-%d_%H.%M.%S}'.format( date=datetime.datetime.now())

    @staticmethod
    def get_today_string(day_delta : int = 0):
        return '{date:%Y-%m-%d}'.format( date=datetime.datetime.now() + datetime.timedelta(days=day_delta))

    @staticmethod
    def random_string(length = 5):
        return ''.join(random.choice(string.ascii_lowercase) for i in range(length))