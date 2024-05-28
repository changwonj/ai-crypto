import pandas as pd
from os import walk
import re

def calc_mid_price(bid_levels, ask_levels):
    mid_price = (bid_levels['price'].max() + ask_levels['price'].min()) / 2
    return mid_price

def calc_book_imbalance(params, bid_levels, ask_levels, var, mid_price):

    ratio, level, interval = params
        
    _flag = var['_flag']
        
    if _flag: #skipping first line
        var['_flag'] = False
        return 0.0

    quant_v_bid = bid_levels.quantity**ratio
    price_v_bid = bid_levels.price * quant_v_bid

    quant_v_ask = ask_levels.quantity**ratio
    price_v_ask = ask_levels.price * quant_v_ask
        
    ask_qty = quant_v_ask.values.sum()
    bid_px = price_v_bid.values.sum()
    bid_qty = quant_v_bid.values.sum()
    ask_px = price_v_ask.values.sum()
    bid_ask_spread = interval
        
    book_price = 0 #because of warning, divisible by 0
    if bid_qty > 0 and ask_qty > 0:
        book_price = (((ask_qty*bid_px)/bid_qty) + ((bid_qty*ask_px)/ask_qty)) / (bid_qty+ask_qty)
        
    indicator_value = (book_price - mid_price) / bid_ask_spread

    return indicator_value

def create_features_df(orderbook):
    df_book = pd.read_csv(orderbook)

    df_book_group = df_book.groupby("timestamp")

    features = []

    var = {'_flag': True}

    for timestamp, group in df_book_group:
        
        bid_levels = group[group['type'] == 0]
        ask_levels = group[group['type'] == 1]

        mid_price = calc_mid_price(bid_levels, ask_levels)

        param = 0.2, 5, 1 #ratio, level, interval

        book_imbalance = calc_book_imbalance(param, bid_levels, ask_levels, var, mid_price)

        features.append({
            'timestamp': timestamp,
            'mid_price': mid_price,
            'book_imbalance': book_imbalance
        })

    df_features = pd.DataFrame(features, columns=['timestamp', 'mid_price', 'book_imbalance'])

    return df_features

# get list of filenames
filenames = next(walk("./"), (None, None, []))[2]

# match filenames to regex pattern for orderbook csv files
pattern = r'^book.*\.csv$'

regex = re.compile(pattern)

orderbooks = [filename for filename in filenames if regex.match(filename)]

for orderbook in orderbooks:
    df_features = create_features_df(orderbook)
    
    pattern = r'^book-(\d{4}-\d{2}-\d{2})-([^-]+-[^.]+)\.csv$'

    regex = re.compile(pattern)

    match = regex.match(orderbook)

    date = match.group(1)
    exchange_symbol = match.group(2)

    df_features.to_csv(f"{date}-{exchange_symbol}-feature.csv", index=False)