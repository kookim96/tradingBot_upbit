import pyupbit
import pandas as pd
import datetime
import time
import backtest
import judge

def login():
    with open("./api_upbit.txt") as f:
        lines = f.readlines()
        access = lines[0].strip()
        secret = lines[1].strip()
    upbit = pyupbit.Upbit(access, secret)

    return upbit

def get_sell_df(ticker):
    try:
        data = pyupbit.get_ohlcv(ticker, interval='minute240', count=8000).reset_index().rename(columns={'index':'date'})
    except Exception as e:
        print(ticker, ': 봉 데이터 불러오기 오류, 상장폐지 가능성 존재(sell_data함수)', e)
        return 0
    return data

def get_df(ticker):
    try:
        data = pyupbit.get_ohlcv(ticker, interval='minute240', count=8000).reset_index().rename(columns={'index':'date'})
    except Exception as e:
        print(ticker, ': 봉 데이터 불러오기 오류, 상장폐지 가능성 존재(get_df함수)', e)
    return data

def buy(upbit, ticker, kelly):
    price = upbit.get_balance_t('KRW')
    price = price*kelly
    try:
        upbit.buy_market_order(ticker, price)
        print('결론 : ' + ticker + ' 구매 완료!!')
    except Exception as e:
        print(ticker, '구매오류:', e)
    print()

def sell(upbit, ticker, volume):
    try:
        upbit.sell_market_order(ticker, volume)
        print('결론' + ticker + ' 판매 완료!!')
    except Exception as e:
        print(ticker, '판매오류', e)
    print()

def trade_time():
    now = datetime.datetime.now()
    now = str(now)[11:13]
    if now == '01' or now == '05' or now == '09' or now == '13' or now == '17' or now == '21':
        return True
    return False

def test_time():##
    now = datetime.datetime.now()
    now = str(now)[11:13]
    if now == '00' or now == '04' or now == '08' or now == '12' or now == '16' or now == '20':
        return True
    return False

def get_own_tickers(upbit):
    own = upbit.get_balances()
    owning = []
    for i in range(len(own)):
        if own[i]['currency'] != 'KRW':
            owning.append(own[i]['currency'])
    return owning

def make_universe():
    print('종목선택 중')
    universe = []
    upbit = login()
    tickers = pyupbit.get_tickers('KRW')

    organize = pd.DataFrame(columns=['name', 'profit', 'loss', 'pro_aver', 'dam_aver', 'winrate', 'ratio', 'kelly'])
    for i in range(len(tickers)):
        data = get_df(tickers[i])
        data = backtest.get_macd(data)
        orga, kelly, state_2, win_rate= backtest.long_backtest(data, tickers[i])
        organize = organize.append(orga, ignore_index=True)

    for i in range(0, len(organize)):
        if organize.loc[i, 'winrate'] >= 0.4:
            if organize.loc[i, 'dam_aver'] > 0.95:
                if organize.loc[i, 'kelly'] > 0.1:
                    universe.append(organize.loc[i, 'name'])
    return universe


def sub_main(worlds):
    def trade(upbit, whom):
        tickers = worlds
        own = get_own_tickers(upbit)
        print(whom, '거래 전 보유: ', own)
        print(whom, '매도판단 시작')
        for k in range(len(own)):
            ticker_own = 'KRW-' + own[k]
            data_sell = get_sell_df(ticker_own)
            if type(data_sell) == int:
                continue
            data_sell = backtest.get_macd(data_sell)
            balance = upbit.get_balance_t(ticker_own)
            if judge.judge_long_terminate(data_sell, ticker_own):
                sell(upbit, ticker_own, balance)
        print('매수판단 시작')
        for i in range(len(tickers)):
            data = get_df(tickers[i])
            data = backtest.get_macd(data)

            if tickers[i][4:] in own:
                continue
            else:
                if judge.judge_long(data, tickers[i]):
                    orga, kelly, state, win = backtest.long_backtest(data, tickers[i])
                    if kelly >= 0.1 and state != 'long':
                        buy(upbit, tickers[i], kelly)
                        print('state 확인: ', state)
                    else:
                        print('결론 :', tickers[i], '매수기준 미충족 -> kelly: ', kelly, '/ state: ', state)
                    del data
                    continue
                else:
                    del data
                    continue
        time.sleep(2)
        own2 = get_own_tickers(upbit)
        print(whom,'거래 후 보유: ', own2)
    if trade_time() == True:##
        time.sleep(60)
        sh = login()
        trade(sh, '(SH)')
        return worlds
    elif test_time() == True:
        worlds = make_universe()
        print(worlds)
        return worlds
    else:
        print('worlds:', worlds)
        print('매매시간이 아닙니다.')
        return worlds


def main():
    worlds = make_universe()
    now = datetime.datetime.now()
    ago = datetime.datetime(now.year, now.month, now.day, now.hour) + datetime.timedelta(hours = 1)

    while True:
        try:
            now = datetime.datetime.now()
            if ago < now < ago + datetime.timedelta(minutes=30):
                now = datetime.datetime.now()
                ago = datetime.datetime(now.year, now.month, now.day, now.hour) + datetime.timedelta(hours = 1)
                worlds = sub_main(worlds)
            print('(Upbit)', now, "vs", ago)
        except Exception as e:
            print('에러발생', e)
        time.sleep(60)

def test():
    #worlds = make_universe()
    worlds = ['KRW-BTC']
    time.sleep(2)
    now = datetime.datetime.now()
    ago = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute) + datetime.timedelta(minutes = 1)

    while True:
        try:
            now = datetime.datetime.now()
            if ago < now :##테스트용
                now = datetime.datetime.now()
                ago = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute) + datetime.timedelta(minutes = 1)
                sub_main(worlds)
            print('(Upbit)', now, "vs", ago)
        except Exception as e:
            print('메인 문 에러발생', e)
        time.sleep(1)

test()
main()

#pyinstaller -F main.py
