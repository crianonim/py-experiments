import json
from pprint import pprint

from confluent_kafka import Consumer

c = Consumer({
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'mygroup9',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['trzeci'])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))
    pprint(msg)
    print("TYPE :",type(msg))
    pprint(dir(msg))
    print("headers")
    pprint(msg.headers())
    print("value")
    value = msg.value()
    pprint(value)
    print("TYPE :", type(value))
    pprint(dir(value))
    print(value.decode('utf-8'))

c.close()
