import os
from pandas import DataFrame
import pandas as pd
import functools
import multiprocessing as mp
from os import listdir
from os.path import isfile, join
from pathlib import Path
import time
import configparser

config = configparser.ConfigParser()
config.read(os.path.relpath("config.ini"))
# CACHE_DIR = '/'.format(os.path.dirname(__file__), os.sep, os.sep, '.data-cache', os.sep)

CACHE_DIR = config['cache']['cache_dir']


class Cacher(object):
    def __init__(self):
        self.make_dirs()
        self.memory_cache = {}

    def get_cache(self, h):
        d = self.get_memory_cache(h)
        if d is None:
            d = self.static_get_cache(h)
            if d is not None:
                self.set_memory_cache(h, d)
        return d

    def get_memory_cache(self, h):
        if h in self.memory_cache.keys():
            print('h', end='')
            return self.memory_cache[h]
        else:
            return None

    def set_memory_cache(self, h, d):
        self.memory_cache[h] = d

    def _load_cache_file(self, filename):
        h = filename
        path = join(CACHE_DIR, filename)
        df = pd.read_pickle(path)
        return h, df
        # self.set_memory_cache(h, df)

    def load_cache(self):

        start = time.time()
        pool = mp.Pool(mp.cpu_count())
        files = [f for f in listdir(CACHE_DIR) if isfile(join(CACHE_DIR, f))]
        results = pool.map(self._load_cache_file, files)
        pool.close()
        pool.join()
        for h, df in results:
            self.set_cache(h, df)
            self.set_memory_cache(h, df)

        end = time.time()
        print('load_cache took {} seconds'.format((end - start)))
        return results

    @staticmethod
    def make_dirs():
        os.makedirs(CACHE_DIR, exist_ok=True)

    @staticmethod
    def static_get_cache(hash: str) -> DataFrame:
        path = '{}{}{}'.format(CACHE_DIR, os.sep, hash)
        if os.path.exists(path):
            return pd.read_pickle(path)
        else:
            return None
            # Get OHLC for ticker

    @staticmethod
    def set_cache(hash: str, df: DataFrame) -> None:
        path = '{}{}{}'.format(CACHE_DIR, os.sep, hash)
        df.to_pickle(path)

    @staticmethod
    def create_hash(*args) -> str:
        l = [x for x in args]
        h = functools.reduce(lambda x, y: str(x) + str(y), l)
        return h
