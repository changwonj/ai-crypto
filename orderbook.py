import time
import datetime
import requests
import pandas as pd

# Initialize date to yesterday => triggers new CSV file creation in line 26 
init_date = datetime.date.today() - datetime.timedelta(days = 1)

while(1):
    
    book = {}
    response = requests.get('https://api.bithumb.com/public/orderbook/BTC_KRW/?count=5')

    # If bithumb API response is not OK, wait 0.5s and try again
    if(response.status_code != 200):
        time.sleep(0.5)
        continue

    book = response.json()

    data = book['data']

    cur_date = datetime.date.today()
    
    # When date changes, create new CSV file for new date with appropriate headers
    if (init_date != cur_date):
        df = pd.DataFrame(columns=['price', 'quantity', 'type', 'timestamp'])
        df.to_csv(f"book-{cur_date}-bithumb-BTC.csv", mode='w', index=False, header=True)
        init_date = cur_date
    
    bids = (pd.DataFrame(data['bids'])).apply(pd.to_numeric,errors='ignore')
    bids.sort_values('price', ascending=False, inplace=True)
    bids = bids.reset_index(); del bids['index']
    bids['type'] = 0
    
    asks = (pd.DataFrame(data['asks'])).apply(pd.to_numeric,errors='ignore')
    asks.sort_values('price', ascending=True, inplace=True)
    asks['type'] = 1 

    df = pd.concat([bids, asks], ignore_index=True)
    
    timestamp = datetime.datetime.now()
    req_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    df['quantity'] = df['quantity'].round(decimals=4)
    df['timestamp'] = req_timestamp

    df.to_csv(f"book-{cur_date}-bithumb-BTC.csv", mode='a', index=False, header=False)

    time.sleep(2.9)