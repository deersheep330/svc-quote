from quote.fugle import Fugle
import asyncio
from datetime import date, timedelta, datetime
import grpc

from quote.utils import get_grpc_hostname
from api.protos import database_pb2_grpc
from api.protos.protobuf_datatype_utils import datetime_to_timestamp

if __name__ == '__main__':

    channel = grpc.insecure_channel(f'{get_grpc_hostname()}:6565')
    stub = database_pb2_grpc.DatabaseStub(channel)

    over_boughts = []
    over_solds = []
    _datetime = datetime.now()
    retry = 0
    max_retry = 7

    while len(over_boughts) == 0 or len(over_solds) == 0:
        print(f'try to get date for datetime = {_datetime}')
        res = stub.query_twse_over_bought_by_date(datetime_to_timestamp(_datetime))
        over_boughts = list(res)
        res = stub.query_twse_over_sold_by_date(datetime_to_timestamp(_datetime))
        over_solds = list(res)
        _datetime -= timedelta(days=1)
        retry += 1
        if retry > max_retry:
            break

    if len(over_boughts) == 0 or len(over_solds) == 0:
        raise Exception('Cannot get TWSE oversold/overbought records')
    else:
        print(f'over_boughts: {[item.symbol for item in over_boughts]}')
        print(f'over_solds: {[item.symbol for item in over_solds]}')

    symbols = []
    tasks = []
    for ele in over_boughts:
        symbols.append(Fugle('overbought', ele.symbol))
        tasks.append(symbols[-1].exec())

    for ele in over_solds:
        symbols.append(Fugle('oversold', ele.symbol))
        tasks.append(symbols[-1].exec())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    for symbol in symbols:
        symbol.dump_to_file()
        symbol.save_to_db()
