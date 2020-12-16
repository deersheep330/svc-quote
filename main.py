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

    while len(over_boughts) == 0 or len(over_solds) == 0:
        print(f'date = {_date}')
        over_boughts = session.query(TwseOverBought).filter_by(date=_date).all()
        over_solds = session.query(TwseOverSold).filter_by(date=_date).all()
        print(over_boughts)
        _date -= timedelta(days=1)

    print(over_boughts)
'''
    test = Fugle('2303')
    #test.exec()
    test.quote()
    test.dump_to_file()
'''