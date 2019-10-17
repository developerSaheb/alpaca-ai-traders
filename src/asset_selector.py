#!/usr/bin/env python
# -*- coding: utf-8 -*-
from alpaca_functions import bullish_candlestick_patterns, time_formatter
from src.edgar_interface import EdgarInterface
import pandas as pd
import json
import time
import sys


class AssetSelector:

    def __init__(self, alpaca_api_interface, edgar_token=None):

        if not alpaca_api_interface or alpaca_api_interface is None:
            raise ValueError("Alpaca API interface instance required")

        self.api            = alpaca_api_interface
        self.account        = self.api.get_account()
        self.buying_power   = self.account.buying_power
        self.edgar_token    = None

        if edgar_token is not None:
            self.edgar_token = edgar_token

    def get_assets_by_candlestick_pattern(self, backdate=None):

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        # Check if our account is restricted from trading.
        if self.account.trading_blocked:
            print("Account is currently restricted from trading.")
            sys.exit(-1)

        # Check how much money we can use to open new positions.
        print("${} is available as buying power.".format(self.buying_power))

        active_assets = self.api.list_assets(status="active")

        # Filter the assets down to just those on NASDAQ.
        assets = [a for a in active_assets if a.tradable and a.shortable and a.marginable and a.easy_to_borrow]
        bullish_to_compare  = dict()
        bearish_to_compare  = dict()
        for i in assets:

            symbol          = i.symbol
            start           = backdate
            barset          = self.api.get_barset(symbol, "1D", after=start)
            symbol_bars     = barset[symbol]

            df              = pd.DataFrame()
            df["time"]      = [bar.t for bar in symbol_bars if bar is not None]
            df["open"]      = [bar.o for bar in symbol_bars if bar is not None]
            df["high"]      = [bar.h for bar in symbol_bars if bar is not None]
            df["low"]       = [bar.l for bar in symbol_bars if bar is not None]
            df["close"]     = [bar.c for bar in symbol_bars if bar is not None]
            df["volume"]    = [bar.v for bar in symbol_bars if bar is not None]

            pattern         = bullish_candlestick_patterns(df.iloc[-3], df.iloc[-2], df.iloc[-1])

            if pattern is None:
                continue

            if pattern in ["hammer", "inverseHammer"]:
                bullish_to_compare[symbol] = df

            if pattern in ["bullishEngulfing", "piercingLine", "morningStar", "threeWhiteSoldiers"]:
                bearish_to_compare[symbol] = df

            if len(bearish_to_compare) is 5 or len(bullish_to_compare) is 5:
                if len(bearish_to_compare) > len(bullish_to_compare):
                    return bearish_to_compare
                elif len(bullish_to_compare) > len(bearish_to_compare):
                    return bullish_to_compare

    def get_assets_with_8k_filings(self, backdate=None):

        if not self.edgar_token or self.edgar_token is None:
            raise NotImplementedError

        if not backdate or backdate is None:
            # backdate = time_formatter(time.time() - 604800, time_format="%Y-%m-%d")

            # using a longer window only for debugging purposes -- just to make sure I have results quickly
            backdate = time_formatter(time.time() - (604800 * 26), time_format="%Y-%m-%d")

        # Check if our account is restricted from trading.
        if self.account.trading_blocked:
            print("Account is currently restricted from trading.")
            sys.exit(-1)

        # Check how much money we can use to open new positions.
        print("${} is available as buying power.".format(self.buying_power))

        date = time_formatter(time.time(), time_format="%Y-%m-%d")

        ei = EdgarInterface(self.edgar_token)

        active_assets = self.api.list_assets(status="active")

        # Filter the assets down to just those on NASDAQ.
        assets = [a for a in active_assets if a.tradable and a.shortable and a.marginable and a.easy_to_borrow]
        assets_with_recent_filings = dict()

        print("Going through assets looking for firms with recent SEC filings")
        for i in assets:

            symbol          = i.symbol
            start           = backdate

            filings         = ei.get_sec_filings(symbol, start, date, form_type="8-K")

            # If none are found, lengthen the lookback window a couple times
            if filings["total"] is 0:
                print("No recent filings found for {}. Looking back 2 weeks".format(symbol))
                start = time_formatter(time.time() - (604800 * 2), time_format="%Y-%m-%d")
                filings = ei.get_sec_filings(symbol, start, date, form_type="8-K")

            if filings["total"] is 0:
                print("No filings found. Looking back 4 weeks")
                start = time_formatter(time.time() - (604800 * 4), time_format="%Y-%m-%d")
                filings = ei.get_sec_filings(symbol, start, date, form_type="8-K")

            if filings["total"] > 0:
                print("\tAdded:", i.symbol, " symbols:", len(assets_with_recent_filings.keys()) + 1)
                filings = json.dumps(filings)
                assets_with_recent_filings[symbol] = filings

            if len(assets_with_recent_filings.keys()) >= 5:
                break
            else:
                continue

        assets_to_trade = dict()

        for i in assets_with_recent_filings.keys():
            # I think I need my original 13 week window here for consistency with get_assets_by_candlestick_pattern
            backdate        = time_formatter(time.time() - (604800 * 13))

            symbol          = i.symbol
            start           = backdate
            barset          = self.api.get_barset(symbol, "1D", after=start)
            symbol_bars     = barset[symbol]

            df              = pd.DataFrame()
            df["time"]      = [bar.t for bar in symbol_bars if bar is not None]
            df["open"]      = [bar.o for bar in symbol_bars if bar is not None]
            df["high"]      = [bar.h for bar in symbol_bars if bar is not None]
            df["low"]       = [bar.l for bar in symbol_bars if bar is not None]
            df["close"]     = [bar.c for bar in symbol_bars if bar is not None]
            df["volume"]    = [bar.v for bar in symbol_bars if bar is not None]

            assets_to_trade[symbol] = df

        return assets_to_trade
