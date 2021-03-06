import alpaca_trade_api as api
import pandas as pd
import os
import numpy as np
from tqdm import tqdm



if __name__ == '__main__':
    
    # hard coded tickers
    tickers = ['TSLA', 'AAPL', 'NVDA', 'GS', 'JPM', 'V', 'MRK', 'PFE', 'JNJ', 'XOM', 'CVX', 'DVN']

    # connect to API
    ALPACA_KEY = 'PKF1UA7IOK2GNIOZJCCE'
    ALPACA_SECRET_KEY = 'qoUq6tjPOwpwDld6DfjTvov5q0bAj0KvvHnUSUDx'
    rest = api.REST(ALPACA_KEY, ALPACA_SECRET_KEY)


    # creates a data folder with a number tag if extras exist
    if not os.path.exists('data'):
        os.mkdir('data')
        
    # create a clean and raw dir
    if not os.path.exists('data/raw_data'):
        os.mkdir('data/raw_data')

    if not os.path.exists('data/clean_data'):
        os.mkdir('data/clean_data')
        
    # retrieve data as far back as possible. Constant end date to remain consistent
    data = []
    for ticker in tqdm( tickers, desc = 'Tickers'):
        
        ohlc = rest.get_bars(ticker, timeframe = api.TimeFrame(1, unit= api.TimeFrameUnit('Hour')), start = '2018-01-01', end = '2022-01-01', adjustment = 'all').df
        
        # save this raw data
        ohlc.to_csv(f'data/raw_data/{ticker}.csv', index = True, header = True)
        
        # clean Nans
        ohlc.fillna(method = 'ffill', inplace = True)
        ohlc.fillna(method = 'bfill', inplace = True)
        ohlc.dropna(axis = 0, inplace = True)
        
        # compute log returns
        ohlc['log_returns'] = np.log(ohlc.close) - np.log(ohlc.close.shift(1))
        
        # first value is now a nan
        ohlc.dropna(axis = 0, inplace = True)
        
        # only include correct time period from 9:00AM - 4:00 PM
        ohlc = ohlc.between_time('09:00', '16:00', inclusive = 'left')
        
        data.append(ohlc[['close','log_returns']])
    
    all_data = pd.concat(data, axis = 1, join = 'outer')
    all_data.fillna(method = 'ffill', inplace = True)
    all_data.dropna(axis = 0, inplace = True)
    
    col_nums = 0
    for ticker in tqdm(tickers, desc = 'Saving Clean data'):
        #save this clean data
        ohlc = all_data.iloc[:, col_nums:col_nums+2]
        ohlc.to_csv(f'data/clean_data/{ticker}.csv', index = True, header = True)
        col_nums += 2
        
        