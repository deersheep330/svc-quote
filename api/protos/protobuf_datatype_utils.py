import datetime

from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp

def datetime_to_timestamp(_datetime):
    # _datetime = datetime.datetime.now() - datetime.timedelta(days=180)
    if _datetime is None:
        return None
    else:
        timestamp = Timestamp()
        timestamp.FromDatetime(_datetime)
        return timestamp
