from quote.utils import get_api_token

if __name__ == '__main__':

    token = get_api_token()
    print(token)

    #url = 'https://api.fugle.tw/realtime/v0/intraday/quote?symbolId=2330&apiToken={}'