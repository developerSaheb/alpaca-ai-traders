#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import time_formatter, set_candlestick_df
from requests.exceptions import HTTPError
from pandas.errors import EmptyDataError
from finta import TA
import time


class IndicatorException(Exception):
    pass


class Indicators:

    def __init__(self, alpaca_api_interface, dataframe=None):

        if not alpaca_api_interface or alpaca_api_interface is None:
            raise ValueError("Alpaca API interface instance required")
        self.api            = alpaca_api_interface
        self.account        = self.api.get_account()
        self.buying_power   = self.account.buying_power
        self.dataframe      = dataframe

    def get_all_asset_indicators(self):
        """Loop through collection of assets and append their indicators to the dataframe.

        :return: A pandas dataframe of ticker dataframes for each asset.
        """
        for ticker in self.dataframe.keys():
            try:
                self.dataframe[ticker] = self.get_ticker_indicators(ticker)
            except EmptyDataError:
                raise EmptyDataError
            except IndicatorException:
                raise IndicatorException
            else:
                continue
        return self.dataframe

    def get_ticker_indicators(self, ticker, backdate=None):
        """Given a ticker symbol and a backdate, calculate indicator values and add them to a dataframe.

        :param ticker: A stock ticker value
        :param backdate: A date to look back. Will default to 13 weeks ago (1 quarter) if None.
        :return: a pandas dataframe with OHLC + indicator values.
        """
        if not ticker or ticker is None:
            raise ValueError("Invalid ticker value")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))

        bars                        = self.get_bars(ticker, backdate)
        data                        = set_candlestick_df(bars)

        # grab individual indicator values
        sma                         = self.get_sma(data)
        smm                         = self.get_smm(data)
        ssma                        = self.get_ssma(data)
        ema                         = self.get_ema(data)
        dema                        = self.get_dema(data)
        tema                        = self.get_tema(data)
        trima                       = self.get_trima(data)
        trix                        = self.get_trix(data)
        vama                        = self.get_vama(data)
        er                          = self.get_er(data)
        kama                        = self.get_kama(data)
        zlema                       = self.get_zlema(data)
        wma                         = self.get_wma(data)
        hma                         = self.get_hma(data)
        # evwma                       = self.get_evwma(data)
        vwap                        = self.get_vwap(data)
        smma                        = self.get_smma(data)
        macd                        = self.get_macd(data)
        ppo                         = self.get_ppo(data)
        vwmacd                      = self.get_vwmacd(data)
        # evmacd                      = self.get_evmacd(data)
        mom                         = self.get_mom(data)
        roc                         = self.get_roc(data)
        rsi                         = self.get_rsi(data)
        ift_rsi                     = self.get_ift_rsi(data)
        tr                          = self.get_tr(data)
        atr                         = self.get_atr(data)
        sar                         = self.get_sar(data)
        bbands                      = self.get_bbands(data)
        bandwidth                   = self.get_bbandwidth(data)
        percent_b                   = self.get_percent_b(data)
        kc                          = self.get_kc(data)
        # do                          = self.get_do(data)
        # dmi                         = self.get_dmi(data)
        adx                         = self.get_adx(data)
        mfi                         = self.get_mfi(data)
        stoch                       = self.get_stoch(data)
        vzo                         = self.get_vzo(data)
        apz                         = self.get_apz(data)
        # separate indicators that consist of multiple values
        _macds                      = macd["MACD"]
        _signals                    = macd["SIGNAL"]
        _ppo                        = ppo["PPO"]
        _pposig                     = ppo["SIGNAL"]
        _ppohist                    = ppo["HISTO"]
        _vmacds                     = vwmacd["MACD"]
        _vsignals                   = vwmacd["SIGNAL"]
        # _evmacds                    = evmacd["MACD"]
        # _evsignals                  = evmacd["SIGNAL"]
        _bb_up                      = bbands["BB_UPPER"]
        _bb_mid                     = bbands["BB_MIDDLE"]
        _bb_low                     = bbands["BB_LOWER"]
        _kc_upper                   = kc["KC_UPPER"]
        _kc_lower                   = kc["KC_LOWER"]
        # _do_upper                   = do["UPPER"]
        # _do_middle                  = do["MIDDLE"]
        # _do_lower                   = do["LOWER"]
        # _dmi_p                      = dmi["DI+"]
        # _dmi_m                      = dmi["DI-"]
        _apz_u                      = apz["UPPER"]
        _apz_l                      = apz["LOWER"]
        # set dataframe values we want to return
        data["sma"]                 = sma
        data["smm"]                 = smm
        data["ssma"]                = ssma
        data["ema"]                 = ema
        data["dema"]                = dema
        data["tema"]                = tema
        data["trima"]               = trima
        data["trix"]                = trix
        data["vama"]                = vama
        data["er"]                  = er
        data["kama"]                = kama
        data["zlema"]               = zlema
        data["wma"]                 = wma
        data["hma"]                 = hma
        # data["evwma"]               = evwma
        data["vwap"]                = vwap
        data["smma"]                = smma
        data["macd"]                = _macds
        data["signal"]              = _signals
        data["ppo"]                 = _ppo
        data["ppo_sig"]             = _pposig
        data["ppo_histo"]           = _ppohist
        data["vwmacd"]              = _vmacds
        data["vwsignal"]            = _vsignals
        # data["evmacd"]              = _evmacds
        # data["evsignal"]            = _evsignals
        data["mom"]                 = mom
        data["roc"]                 = roc
        data["rsi"]                 = rsi
        data["ift_rsi"]             = ift_rsi
        data["tr"]                  = tr
        data["atr"]                 = atr
        data["sar"]                 = sar
        data["bb_up"]               = _bb_up
        data["bb_mid"]              = _bb_mid
        data["bb_low"]              = _bb_low
        data["bandwidth"]           = bandwidth
        data["percent_b"]           = percent_b
        data["kc_upper"]            = _kc_upper
        data["kc_lower"]            = _kc_lower
        # data["do_upper"]            = _do_upper
        # data["do_middle"]           = _do_middle
        # data["do_lower"]            = _do_lower
        # data["dmi_p"]               = _dmi_p
        # data["dmi_m"]               = _dmi_m
        data["adx"]                 = adx
        data["mfi"]                 = mfi
        data["stoch"]               = stoch
        data["vzo"]                 = vzo
        data["apz_u"]               = _apz_u
        data["apz_l"]               = _apz_l

        return data

    def get_bars(self, ticker, backdate=None):
        """Get bars for a ticker symbol

        :param ticker: a stock ticker symbol
        :param backdate: start of the historic data lookup period. If none, defaults to the last 13 weeks (1 quarter)
        :return: dataframe built from barset objects, including indicators
        """
        if not ticker or ticker is None:
            raise ValueError("Invalid ticker value")

        if not backdate or backdate is None:
            backdate = time_formatter(time.time() - (604800 * 13))
        bars = None
        try:
            bars = self.api.get_barset(ticker, "1D", after=backdate)[ticker]
        except HTTPError:
            print("Retrying...")
            time.sleep(3)
            try:
                bars = self.api.get_barset(ticker, "1D", after=backdate)[ticker]
            except HTTPError:
                raise HTTPError
        finally:
            return bars

    @staticmethod
    def get_sma(data):
        """Calculate the simple moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.SMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_smm(data):
        """Calculate the simple moving median for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.SMM(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_ssma(data):
        """Calculate the SMOOTHED simple moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.SSMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_ema(data):
        """Calculate the exponential moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.EMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_dema(data):
        """Calculate the double exponential moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.DEMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_tema(data):
        """Calculate the triple exponential moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.TEMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_trima(data):
        """Calculate the triangular moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.TRIMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_trix(data):
        """Calculate the triple exponential moving average oscillator for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.TRIX(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vama(data):
        """Calculate the volume adjusted moving average for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.VAMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_er(data):
        """Calculate the Kaufman efficiency ratio for values of given dataframe.

        Example
            bullish: +0.67
            bearish: -0.67

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.ER(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_kama(data):
        """Calculate the Kaufman adaptive moving avarage for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.KAMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_zlema(data):
        """Calculate the zero log exponential moving avarage for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.ZLEMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_wma(data):
        """Calculate the weighted moving avarage for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.WMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_hma(data):
        """Calculate the Hull moving avarage for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.HMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_evwma(data):
        """Calculate the EVWMA for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.EVWMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vwap(data):
        """Calculate the volume weighted average price for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.VWAP(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_smma(data):
        """Calculate the smoothed moving avarage for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.SMMA(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_macd(data):
        """Calculate the moving average convergence-divergence for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series with the MACD and signal values
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.MACD(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_ppo(data):
        """Calculate the percentage price oscillator for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series with the PPO and signal values
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.PPO(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vwmacd(data):
        """Calculate the volume-weighted MACD for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series with the VWMACD and signal values
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.VW_MACD(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_evmacd(data):
        """Calculate the elastic volume-weighted MACD for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a concatenated Pandas series with the EVMACD and signal values
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.EV_MACD(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_mom(data):
        """Calculate the momentum for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.MOM(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_roc(data):
        """Calculate the rate of change for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.ROC(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_rsi(data):
        """Calculate the relative strength index for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.RSI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_ift_rsi(data):
        """Calculate the Inverse-Fisher Transform on relative strength index for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.IFT_RSI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_tr(data):
        """Calculate the true range for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.TR(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_atr(data):
        """Calculate the average true range for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.ATR(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_sar(data):
        """Calculate the stop and reverse for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.SAR(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_bbands(data):
        """Calculate the Bollinger bands for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.BBANDS(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_bbandwidth(data):
        """Calculate the Bollinger bandwidth for values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.BBWIDTH(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_percent_b(data):
        """Calculate the percent b for Bollinger band values of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.PERCENT_B(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_kc(data):
        """Calculate the Keltner channel of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.KC(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_do(data):
        """Calculate the Donchian channels of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.DO(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_dmi(data):
        """Calculate the directional movement indicator of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.DMI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_adx(data):
        """Calculate the ADX of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.ADX(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_mfi(data):
        """Calculate the money flow index of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.MFI(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_stoch(data):
        """Calculate the stochastic oscillator for given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.STOCH(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_vzo(data):
        """Calculate the volume zone oscillator for given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.VZO(data)
        if result is None:
            raise IndicatorException
        return result

    @staticmethod
    def get_apz(data):
        """Calculate the adaptive price zone of given dataframe.

        :param data: a dataframe in OHLC format
        :return: a Pandas series
        """
        if data is None:
            raise EmptyDataError("Invalid data value")

        result = TA.APZ(data)
        if result is None:
            raise IndicatorException
        return result
