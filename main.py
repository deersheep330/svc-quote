from quote.db import create_engine, get_db_hostname, start_session
from quote.fugle import Fugle
from quote.models import TwseOverBought, TwseOverSold

from datetime import date, timedelta

if __name__ == '__main__':

    engine = create_engine('mysql+pymysql', 'root', 'admin', get_db_hostname(), '3306', 'mydb')
    session = start_session(engine)

    over_boughts = []
    over_solds = []
    _date = date.today()
    retry = 0
    max_retry = 5

    while len(over_boughts) == 0 or len(over_solds) == 0:
        print(f'date = {_date}')
        over_boughts = session.query(TwseOverBought).filter_by(date=_date).all()
        over_solds = session.query(TwseOverSold).filter_by(date=_date).all()
        print(over_boughts)
        _date -= timedelta(days=1)
        retry += 1
        if retry > max_retry:
            break

    if len(over_boughts) == 0 or len(over_solds) == 0:
        raise Exception('Cannot get TWSE oversold/overbought records')

    symbols = []
    for ele in over_boughts + over_solds:
        symbols.append(ele.symbol)
    print(symbols)
'''
    test = Fugle('2303')
    #test.exec()
    test.quote()
    test.dump_to_file()
'''