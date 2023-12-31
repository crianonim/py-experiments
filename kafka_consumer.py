import json
import sys
from pprint import pprint

from confluent_kafka import Consumer




    # pprint(msg)
    # print("TYPE :",type(msg))
    # pprint(dir(msg))
    # print("headers")
    # pprint(msg.headers())
    # print("value")
    # value = msg.value()
    # pprint(value)
    # print("TYPE :", type(value))
    # pprint(dir(value))
    # print(value.decode('utf-8'))

def consume_as_group(group:str="mygroup9"):
    c = Consumer({
        'bootstrap.servers': 'localhost:29092',
        'group.id': group,
        'auto.offset.reset': 'earliest'
    })

    c.subscribe(['trzeci'])
    while True:
        msg = c.poll(5.0)

        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        print('Received message: {}'.format(msg.value().decode('utf-8')))
        print(f' at partition {msg.partition()}')

    c.close()

if __name__ == '__main__':
    group = "mygroup9" if len(sys.argv)<2 else sys.argv[1]
    consume_as_group(group)
