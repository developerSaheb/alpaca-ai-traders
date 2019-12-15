import os
from src.util.StringUtil import StringUtil
from src.util.FileUtil import FileUtil as fu
class TradeLogger(object):

    def __init__(self, path, headers):
        self.sessionId = StringUtil.get_now_string()
        self.path = '{}{}{}{}'.format(path, os.sep, self.sessionId, os.sep)
        self.headers = headers

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.all_logs_path = self.path + os.sep + 'ALL_LOGS.csv'
        fu.write_file(self.all_logs_path, headers + '\n')
        print("Logging to \n" + self.path)

    def log(self, ticker, str):
        file_path = self.path + os.sep + ticker + '.csv'
        if not os.path.exists(file_path):
            fu.write_file(file_path, self.headers + '\n')
        fu.append_to_file(file_path, str + '\n')
        fu.append_to_file(self.all_logs_path, str + '\n')
