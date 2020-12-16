from quote.fugle import Fugle

if __name__ == '__main__':

    test = Fugle('2303')
    test.exec()
    test.dump_to_file()

    #url = 'https://api.fugle.tw/realtime/v0/intraday/quote?symbolId=2330&apiToken={}'