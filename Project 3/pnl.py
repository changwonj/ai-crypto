import pandas as pd
import numpy as np


df = pd.read_csv("./ai-crypto-project-3-live-btc-krw.csv")

# set quantity to positive or negative depending on depending on side (buy/sell)
df["adjusted_qty"] = np.where(df["side"] == 0, df["quantity"], df["quantity"] * -1)

df["cumulative_qty"] = df["adjusted_qty"].cumsum()

df["profit"] = df['price'] * df['adjusted_qty'] * -1

# profit with deduction of fee
df["profit_fees"] = df['price'] * df['adjusted_qty'] * -1 - df['fee']

# save row numbers where cumulative quantity is close to 0 (mock starting position = 0)
rows_zero_cum_qty = df[df["cumulative_qty"].abs() <= 0.0000001].index.to_numpy()

row_nums = np.insert(rows_zero_cum_qty, 0, 0)

PnL = []

DIVIDER = "--------------------------------------------------------"

print("PnL without considering starting position")
print(f"Profit: {df['profit'].sum()}")
print(f"Profit minus fees: {df['profit_fees'].sum()}")
print(DIVIDER)

print("PnL considering starting position")
print("Rows where cumulative sum of quantity is close to 0:", *rows_zero_cum_qty)

# calculate PnL for time ranges where cumulative sum of quantity is close to 0
for i in range(0, row_nums.size - 1):
    start_row = row_nums[i] if row_nums[i] == 0 else row_nums[i] + 1
    end_row = row_nums[i+1]
    start_time = df.iloc[start_row]['timestamp']
    end_time = df.iloc[end_row]['timestamp']
    profit = df.loc[start_row:end_row, 'profit'].sum()
    profit_fees = df.loc[start_row:end_row, 'profit_fees'].sum()

    print(f"start row: {start_row}, end row: {end_row}")
    print(f"PnL from time {start_time} to {end_time} (rows {start_row} to {end_row})")
    print(f"Profit: {profit}")
    print(f"Profit minus fees: {profit_fees}")
    print(DIVIDER)

    PnL.append({
            'start_time': start_time,
            'end_time': end_time,
            'start_row': start_row,
            'end_row': end_row,
            'profit': profit,
            'profit_fees': profit_fees,
        })

results = pd.DataFrame(PnL, columns=['start_time', 'end_time', 'start_row', 'end_row', 'profit', 'profit_fees'])

# Realized PnL of sold coins, from entire range where cumulative sum of quantity is close to 0
print("Realized PnL")
print(f"Profit: {results['profit'].sum()}")
print(f"Profit minus fees: {results['profit_fees'].sum()}")
print(DIVIDER)

# Unrealized PnL of unsold leftover coins
leftover_coins = df.iloc[-1]['cumulative_qty']
final_price = df.iloc[-1]['price']
unrealized_PnL = leftover_coins * final_price

print(f"Leftover coins: {leftover_coins}")
print(f"Unrealized PnL: {unrealized_PnL}")
print(DIVIDER)

# Total PnL, sum of realized and unrealized PnL
print(f"Total PnL (profit only): {profit + unrealized_PnL}")
print(f"Total PnL (profit minus fees): {profit_fees + unrealized_PnL}")

results.to_csv("pnl-results.csv", index=False)
df.to_csv("ai-crypto-project-3-live-btc-krw-edited.csv", index=False)