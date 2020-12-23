import json

if __name__ == '__main__':
    with open('dump-2317.txt') as f:
        records = json.load(f)
        ask_units = 0
        bid_units = 0
        prev_ask = {
            'price': 0,
            'unit': 0
        }
        prev_bid = {
            'price': 0,
            'unit': 0
        }
        for index, record in enumerate(records):
            # no transaction
            if len(record['bestAsks']) == 0 or len(record['bestBids']) == 0:
                continue
            cur_ask = record['bestAsks'][0]
            cur_bid = record['bestBids'][-1]
            # broken data
            if index != 0 and (cur_ask['price'] == 0 or cur_bid['price'] == 0):
                continue
            # initialize
            if prev_ask['price'] == 0 and prev_bid['price'] == 0 \
               and prev_ask['unit'] == 0 and prev_bid['unit'] == 0:
                prev_ask['price'] = cur_ask['price']
                prev_ask['unit'] = cur_ask['unit']
                prev_bid['price'] = cur_bid['price']
                prev_bid['unit'] = cur_bid['unit']
            else:
                # ask side
                if cur_ask['price'] == prev_ask['price']:
                    if cur_ask['unit'] < prev_ask['unit']:
                        ask_units += prev_ask['unit'] - cur_ask['unit']
                    prev_ask['unit'] = cur_ask['unit']
                elif cur_ask['price'] > prev_ask['price']:
                    ask_units += prev_ask['unit']
                    prev_ask['price'] = cur_ask['price']
                    prev_ask['unit'] = cur_ask['unit']
                elif cur_ask['price'] < prev_ask['price']:
                    prev_ask['price'] = cur_ask['price']
                    prev_ask['unit'] = cur_ask['unit']

                # bid side
                if cur_bid['price'] == prev_bid['price']:
                    if cur_bid['unit'] < prev_bid['unit']:
                        bid_units += prev_bid['unit'] - cur_bid['unit']
                    prev_bid['unit'] = cur_bid['unit']
                elif cur_bid['price'] < prev_bid['price']:
                    bid_units += prev_bid['unit']
                    prev_bid['price'] = cur_bid['price']
                    prev_bid['unit'] = cur_bid['unit']
                elif cur_bid['price'] > prev_bid['price']:
                    prev_bid['price'] = cur_bid['price']
                    prev_bid['unit'] = cur_bid['unit']
        print(ask_units)
        print(bid_units)
