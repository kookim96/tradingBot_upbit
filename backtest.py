import pyupbit
import pandas as pd
import pprint
import datetime

def get_macd(df):
    df = pd.DataFrame(df)


    ma_4 = df['close'].rolling(window=48).mean()

    df = df.assign(ma4 = ma_4)
    return df

def long_algo(data):
    data["state"] = ''
    data["ratio"] = ''

    for i in range(1, len(data)):
        if data.loc[i-1, 'state'] != 'long':
            if data.loc[i - 1, 'close'] > data.loc[i - 1, 'ma4']:
                data.loc[i, 'state'] = 'long'
                buy_price = data.loc[i, 'open']

        else:
            if data.loc[i-1, 'state'] == 'long':
                if data.loc[i-1, 'state'] != 'terminate':
                    data.loc[i, 'state'] = 'long'
            if data.loc[i, 'close'] < data.loc[i, 'ma4']:
                sell_price = data.loc[i, 'close']
                data.loc[i, 'ratio'] = sell_price / buy_price
                data.loc[i, 'state'] = 'terminate'
    return data

def conclude(data, ticker):

    ratio = 1
    baddest = 1
    goodest = 1
    profit = 0
    damage = 0
    pro_ratio = 0
    dam_ratio = 0
    for i in range(0, len(data)):
        if data.loc[i, 'ratio'] != '':
            if data.loc[i, 'ratio'] - 0.00278 > 1:
                profit += 1
                pro_ratio += data.loc[i, 'ratio'] - 0.00278
                if goodest < data.loc[i, 'ratio'] - 0.00278:
                    goodest = data.loc[i, 'ratio'] - 0.00278
            if data.loc[i, 'ratio'] - 0.00278 < 1:
                damage += 1
                dam_ratio += data.loc[i, 'ratio'] - 0.00278
                if baddest > data.loc[i, 'ratio'] - 0.00278:
                    baddest = data.loc[i, 'ratio'] - 0.00278
            ratio *= data.loc[i, 'ratio'] - 0.00278
    if profit != 0 and damage != 0:
        aver_pro = pro_ratio / profit
        aver_dam = dam_ratio / damage
        win_rate = profit / (profit + damage)
    else:
        aver_pro = 0
        aver_dam = 0
        win_rate = 0

    return ratio, aver_pro, aver_dam, win_rate, profit, damage

def print_rate(ticker, ratio, kelly, aver_pro, aver_dam, win_rate, profit, damage):
    print(ticker)
    print('이익횟수: ', profit)
    print('손해횟수: ', damage)
    print('평균 이율:', aver_pro)
    print('평균 손해율:', aver_dam)
    print('승률:', win_rate)
    print('총 이율:', int(ratio * 100), '%')
    print("캘리의 법칙", kelly)

def long_backtest(data, ticker):
    macd_data = get_macd(data)
    result = long_algo(macd_data)
    ratio, aver_pro, aver_dam, win_rate, profit, damage = conclude(result, ticker)

    f_time_2 = result.index[-2]
    state = result.loc[[f_time_2], ['state']]
    state_2 = state['state'].values[0]
    #print(ticker, ': state ->', state_2)

    if win_rate != 0:
        kelly = win_rate - (1-win_rate)/((aver_pro-1)/(1-aver_dam))
    else:
        kelly = 0
    if kelly < 0:
        kelly = 0

    orga = {'name': ticker, 'profit': profit, 'loss': damage, 'pro_aver': aver_pro,
            'dam_aver': aver_dam, 'winrate': win_rate, 'ratio': ratio, 'kelly': kelly}

    #print_rate(ticker, ratio, kelly, aver_pro, aver_dam, win_rate, profit, damage)

    return orga, kelly, state_2, win_rate

# data = pyupbit.get_ohlcv('KRW-ETH', interval='minute240', count=5)
# data = get_macd(data).reset_index().rename(columns={'index':'date'})
# print(data)
# for i in range(1, len(data)):
#     print(data.loc[i, 'date'])
# print(type(data))
# long_backtest(data, 'KRW-ETH')



