#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.indicators import Indicators
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np

class PrepData:

    def __init__(self, alpaca_api_interface, tickers=None, backdate=None):
        if not alpaca_api_interface or alpaca_api_interface is None:
            raise ValueError("[!] Alpaca API interface instance required")
        self.api            = alpaca_api_interface
        self.backdate       = backdate
        self.indicators     = Indicators(self.api)
        self.tickers        = tickers
        self.scaler         = MinMaxScaler()


    def get_raw_data_per_ticker(self):
        """Loop through an array of ticker names.

        :create: CSV files in data/raw/{ticker}.csv
        """
        for ticker in self.tickers:
            ticker_cluster  = self.indicators.get_ticker_indicators(ticker, self.backdate)
            ticker_cluster.to_csv(r'data\raw\{}.csv'.format(ticker), index_label='date')


    def normalize_data(self):
        """Loop through an array of ticker names.

        :create: CSV files in data/processed/{ticker}.csv
        """
        for ticker in self.tickers:
            ticker_cluster          = pd.read_csv(r'data\raw\{}.csv'.format(ticker), index_col='date')

            for key in ticker_cluster.keys():
                to_np               = np.array(ticker_cluster[key])
                to_np               = to_np.reshape(-1,1)
                ticker_cluster[key] = self.scaler.fit_transform(to_np)

            ticker_cluster.to_csv(r'data\processed\{}.csv'.format(ticker), index_label='date')
        
