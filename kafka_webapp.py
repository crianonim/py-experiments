# TO RUN: python -m flask --app kafka_weapp.y run

from flask import Flask, request

from collections.abc import Mapping, Sequence, Iterable, MutableMapping
from concurrent.futures import Future
from pprint import pprint
from confluent_kafka import Consumer
from confluent_kafka import admin, TopicCollection, Uuid, TopicPartitionInfo, ConsumerGroupState, TopicPartition, \
    ConsumerGroupTopicPartitions
from confluent_kafka.admin import BrokerMetadata, TopicMetadata, ClusterMetadata, AdminClient, PartitionMetadata, \
    TopicDescription, ListConsumerGroupsResult, ConsumerGroupListing

a: AdminClient = admin.AdminClient({'bootstrap.servers': 'localhost:29092'})
consumer_group = "kafka_webapp_consumer"

app = Flask(__name__)

cluster_metadata: ClusterMetadata = a.list_topics()
topics: MutableMapping[str, TopicMetadata] = cluster_metadata.topics

topicPartitions: list[TopicPartition] = []
del topics["__consumer_offsets"]

for topic in topics.values():

    for partition in topic.partitions.values():
        topicPartitions.append(TopicPartition(topic.topic, partition.id, offset=0))

pprint(topicPartitions)
changing = a.alter_consumer_group_offsets([ConsumerGroupTopicPartitions(consumer_group, topicPartitions)])
while changing[consumer_group].running():
    print("CHANGING")

print(changing[consumer_group].result())
c = Consumer({
    'bootstrap.servers': 'localhost:29092',
    'group.id': consumer_group,
    'auto.offset.reset': 'earliest'
})

c.subscribe(list(topics.keys()))

messages = []
# exit(0)
while True:
    msg = c.poll()

    if msg is None:
        break
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue
    messages.append(
        (msg.value(), msg.partition(), msg.timestamp(), msg.topic()))
    # print('Received message: {}'.format(msg.value().decode('utf-8')))
    pprint(msg)
    # print("TYPE :", type(msg))
    # pprint(dir(msg))
    # print("headers")
    # pprint(msg.headers())
    # print("value")
    # value = msg.value()
    # pprint(value)
    # print("TYPE :", type(value))
    # pprint(dir(value))
    # print(value.decode('utf-8'))

c.close()

pprint(changing[consumer_group].result())
# a.poll(10)
# exit(0)
# tp0: TopicPartition = TopicPartition("trzeci", 0, offset=0)
# tp1: TopicPartition = TopicPartition("trzeci", 1, offset=0)
# lista: ConsumerGroupTopicPartitions = ConsumerGroupTopicPartitions("mygroup9", [tp0, tp1])
# x = a.alter_consumer_group_offsets([lista])
#

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"


def list_item(i):
    return "<li>" + i + "</li>"


def ul(iterable: Iterable, fn=lambda x: x):
    return f'<ul>{"\n".join((list(map(lambda x: list_item(fn(x)), iterable))))}</ul>'


def show_partition_meta(partition: PartitionMetadata):
    return f'<li class="partition">${partition.id}</li>'


def show_topic_meta(topic: TopicMetadata):
    partitions: Mapping[int, PartitionMetadata] = topic.partitions
    return f"""<div>
    <div>{topic.topic.upper()}</div>
    <details>
     <summary>Partitions</summary>
    {ul(partitions.keys(), str)}
    <details>
    </div>"""
    first_partition: PartitionMetadata = partitions[0]
    topic_error: None = topic.error
    topic_name: str = topic.topic


# @app.route("/topics/<topic>")
# def topic_route(index):


def topics_route():
    return f"""
    <div>
    {ul(topics.keys(), lambda x: x.upper())}
     {ul(topics.values(), show_topic_meta)}
    </div>
    """


def show_message(message):
    m_value, m_partition, m_timestamp, m_topic = message
    return f' {str(m_value)} {str(m_partition)} {str(m_timestamp)} {m_topic}'


@app.route("/messages")
def messages_route():
    return ul(messages, show_message)
