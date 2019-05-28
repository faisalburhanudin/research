# %%
from datetime import datetime

import talib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# %%


def get_stock(symbol: str, start: str = None, end: str = None) -> pd.DataFrame:
    """Get Stock data frame

    Args:
        symbol: stock symbol
        start: start date trading, ex 2019-02-28
        end: end date trading, ex 2019-02-28

    Returns:
        DataFrame Stock
    """

    # download stock from github
    # raw data from repository
    df = pd.read_csv(f'https://raw.githubusercontent.com/faisalburhanudin/idx/master/stocks/{symbol}.csv')

    # convert string Date to DateTime
    df['DateTime'] = pd.DatetimeIndex(df['Date'])
    df['Month'] = pd.DatetimeIndex(df['Date']).month
    df['Year'] = pd.DatetimeIndex(df['Date']).year
    df['Day'] = pd.DatetimeIndex(df['Date']).day

    # limit dataframe start until start date
    if start:
        df = df[df['DateTime'] >= datetime.fromisoformat(start)]

    # limit dataframe until end date
    if end:
        df = df[df['DateTime'] <= datetime.fromisoformat(end)]

    return df


stock = get_stock('BBRI', '2017-01-01')


# %%
def buy_and_hold(stock_df: pd.DataFrame):
    money = 0

    record = []
    df_month = stock_df.groupby(['Year', 'Month'], as_index=False).first()
    for value in df_month.itertuples():
        # deposit money
        money += 1_000_000

        # price per lot
        per_lot = value.Close * 100

        # total share buy
        buy_share = money // per_lot * 100

        # total cost buy
        buy_cost = buy_share * value.Close

        # deduct from money
        money -= buy_cost

        record.append((value.DateTime, money, value.Close, buy_share))

    record = pd.DataFrame(record, columns=['DateTime', 'Money', 'Close', 'Share'])

    record['SumShare'] = record['Share'].expanding().sum()
    record['Value'] = record['SumShare'] * record['Close'] + record['Money']
    return record


record_df = buy_and_hold(stock)


# %%
def golden(stock_df: pd.DataFrame):
    stock_df['MA50'] = talib.SMA(stock_df['Close'], timeperiod=50)
    stock_df['MA200'] = talib.SMA(stock_df['Close'], timeperiod=200)

    money = 0
    record = []
    df_month = stock_df.groupby(['Year', 'Month'], as_index=False).first()
    for value in df_month.itertuples():
        # deposit money
        money += 1_000_000
        buy_share = 0

        if not np.isnan(value.MA50) and not np.isnan(value.MA50):

            # price per lot
            per_lot = value.Close * 100

            # buy stock
            if value.MA50 >= value.MA200:
                # total share buy
                buy_share = money // per_lot * 100

                # total cost buy
                buy_cost = buy_share * value.Close

                # deduct from money
                money -= buy_cost

            # sell stock
            else:
                # calculated total owned share
                own_share = get_owned_share([i[3] for i in record])
                if own_share:
                    buy_share = -own_share
                    money += own_share * per_lot * 100

        record.append((value.DateTime, money, value.Close, buy_share, value.MA50, value.MA200))

    record = pd.DataFrame(record, columns=['DateTime', 'Money', 'Close', 'Share', 'MA50', 'MA200'])

    record['SumShare'] = record['Share'].expanding().sum()
    record['Value'] = record['SumShare'] * record['Close'] + record['Money']
    return record


def get_owned_share(buy_share):
    owned = 0
    for i in reversed(buy_share):
        if i < 0:
            break
        else:
            owned += i

    return owned


golden_df = golden(stock)

# %%
final = pd.DataFrame({
    'DateTime': record_df['DateTime'],
    'buy and hold': record_df['Value'],
    'golden cross': golden_df['Value']
})

final.plot.line(x='DateTime', y=['buy and hold', 'golden cross'])
ax = plt.gca()
ax.ticklabel_format(style='plain', axis='y')
plt.show()
