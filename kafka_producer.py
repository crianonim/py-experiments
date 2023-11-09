import json
from time import sleep

from confluent_kafka import Producer

p = Producer({'bootstrap.servers': 'localhost:29092'})
import message_gen

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))



while True:
    # Trigger any available delivery report callbacks from previous produce() calls
    p.poll(0)
    sender=message_gen.generate_name()
    to=message_gen.generate_name()
    content = message_gen.get_polite_message()
    msg={"to": to,"from":sender,"content":content}
    # Asynchronously produce a message. The delivery report callback will
    # be triggered from the call to poll() above, or flush() below, when the

    # message has been successfully delivered or failed permanently.
    p.produce(topic='trzeci',value= json.dumps(msg).encode('utf-8'),key=to.encode('utf-8'), callback=delivery_report)
    sleep(2)
# Wait for any outstanding messages to be delivered and delivery report
# callbacks to be triggered.
p.flush()
