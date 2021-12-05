import urllib.request
import json
import codecs
import time
import requests
import pandas as pd
import datetime
import pyupbit
import re
import openpyxl

show_title = 1
df = pd.DataFrame()
# last_date 이전 데이터만 출력
# to_date 이후 데이터만 출력
def get_upbit_data(url, last_date, to_date) :
    global show_title
    global df

    fail2GetData = False
    failCnt = 0
    response = ''
    while True:
        try :
            response = requests.get(url)
        except Exception as e:
            print(e)
            time.sleep(20)
            continue
        if str(response) == '<Response [200]>':
            break
        time.sleep(10)
    if ( fail2GetData )  :
        print("Fail to access url")
        exit()


    data = response.json()
    try:
        code = data[0]['code']
    except Exception as c:
        return True
    # if show_title :
    #   show_title = 0
    #   print(code)

    date = ''
    dateKst = ''
    last_date = ''
    #
    for i in range(len(data))  :
        dateKst = data[i]['candleDateTimeKst']
        date = data[i]['candleDateTime']
        if (last_date == '' or last_date > date) :
            if (dateKst >= to_date) :
                simpleDate = dateKst.split('+')
                df = df.append(pd.DataFrame([[simpleDate[0], data[i]['openingPrice'],
                                              data[i]['highPrice'], data[i]['lowPrice'], data[i]['tradePrice'],
                                              data[i]['candleAccTradeVolume']]]),ignore_index=True)
            else :
                break

    return date

def get_coin_data_url(coinName, type, scale, cnt=400) :#카운트 디버깅
    addr = 'https://crix-api-endpoint.upbit.com/v1/crix/candles/'

    if type == 'minutes' :
        basic_url = addr + type + '/' + scale + '?code=CRIX.UPBIT.KRW-' + coinName +'&count='+str(cnt)
    else :
        basic_url = addr + type + '/' + '?code=CRIX.UPBIT.KRW-' + coinName +'&count='+str(cnt)

    return basic_url

def name_column(name, timeframe):
    wb = openpyxl.load_workbook(filename = f"./datafiles_upbit/upbit_{name}_raw_{timeframe}.xlsx", read_only=False, data_only=False)
    sheet = wb.active
    sheet['B1'] = 'date'
    sheet['C1'] = 'open'
    sheet['D1'] = 'high'
    sheet['E1'] = 'low'
    sheet['F1'] = 'close'
    sheet['G1'] = 'vol'
    wb.save(f"./datafiles_upbit/upbit_{name}_raw_{timeframe}.xlsx")
    print(name,'콜롬명 설정 완료')

def coindata_main(ticker, timeframe):
    global df
    df = pd.DataFrame()

    inde = timeframe.find('/')
    if inde != -1:
        minutes = timeframe[inde+1:]
        hours = int(int(minutes)/60)
        timeline = f'{hours}h'
    else:
        timeline = timeframe

    coinName = ticker
    to_date = ''    #2017-09-27형식
    type = timeframe     #minutes/#, days, weeks, months
    scale = '1'
    end = 0
    last_date = ''
    basic_url = get_coin_data_url(coinName, type, scale)
    url = basic_url

    while (1) :
        if get_upbit_data(url, last_date, to_date) != True:
            last_date = get_upbit_data(url, last_date, to_date)
        else:
            break
        tmp1 = last_date.split('T')
        if tmp1[0]  < to_date :
            break
        tmp2 = tmp1[1].split('+')
        target_date = tmp1[0] + ' ' + tmp2[0]
        url = basic_url + '&to=' + target_date    #to=2019-11-27 04:01:00
        time.sleep(3)
    result = df.loc[::-1].reset_index(drop=True)
    result = result.drop_duplicates(0, keep="first")
    result.to_excel(f"./datafiles_upbit/upbit_{ticker}_raw_{timeline}.xlsx")
    name_column(ticker, timeline)

    print(ticker, 'done')


# tickers = pyupbit.get_tickers('KRW')

# for i in range(0, len(tickers)):
#     ticker = tickers[i]
#     ticker = ticker.lower()
#     tic = ticker[4:]
#     print(tic)
#     coindata_main(tic, type='days')

# coindata_main('btc', 'days')


#minutes/#, days, weeks, months
