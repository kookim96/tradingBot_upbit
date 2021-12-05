

def judge_long(data, ticker):
    minus2 = data.index[-2]
    minus3 = data.index[-3]

    if data.loc[minus2, 'close'] > data.loc[minus2, 'ma4']:
        return True

    print(ticker + ' long 진입 대기!!')
    return False

def judge_long_terminate(data, ticker):
    minus2 = data.index[-2]

    if data.loc[minus2, 'close'] < data.loc[minus2, 'ma4']:
        print(ticker + ': long 포지션 종료', '\n')
        return True
    print(ticker + ': long 포지션 유지')
    return False





