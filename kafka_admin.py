from collections.abc import Mapping
from concurrent.futures import Future
from pprint import pprint

from confluent_kafka import admin, TopicCollection, Uuid, TopicPartitionInfo, ConsumerGroupState
from confluent_kafka.admin import BrokerMetadata, TopicMetadata, ClusterMetadata, AdminClient, PartitionMetadata, \
    TopicDescription, ListConsumerGroupsResult, ConsumerGroupListing

a: AdminClient = admin.AdminClient({'bootstrap.servers': 'localhost:29092'})




list_topics: ClusterMetadata = a.list_topics()
topics: Mapping[str, TopicMetadata] = list_topics.topics
mytopic: TopicMetadata = topics['mytopic']
partitions: Mapping[int, PartitionMetadata] = mytopic.partitions
first_partition: PartitionMetadata = partitions[0]
topic_error: None = mytopic.error
topic: str = mytopic.topic
brokers: Mapping[int, BrokerMetadata] = list_topics.brokers
first_broker: BrokerMetadata = brokers[1]
first_broker_host: str = first_broker.host
first_broker_port: int = first_broker.port
first_broker_id: int = first_broker.id
cluster_id: str = list_topics.cluster_id
controller_id: int = list_topics.controller_id
topics_collection: TopicCollection = TopicCollection(['mytopic', 'testowy', 'trzeci'])
topics_collection_names: list[str] = topics_collection.topic_names
topics_description = a.describe_topics(topics_collection)
topics_description_trzeci: Future = topics_description['trzeci']
while topics_description_trzeci.running():
    pass

topics_description_result: TopicDescription = topics_description_trzeci.result()
tdr_auth: None | list = topics_description_result.authorized_operations
tdr_topic_id: Uuid = topics_description_result.topic_id
tdr_parts: list[TopicPartitionInfo] = topics_description_result.partitions
tdr_parts_0: TopicPartitionInfo = tdr_parts[0]

cg: Future = a.list_consumer_groups()
while cg.running():
    pass
cg_result: ListConsumerGroupsResult = cg.result()
cgr_0_group: ConsumerGroupListing = cg_result.valid[0]
cgr_0_group_id: str = cgr_0_group.group_id  # 'mygroup2'
cgr_0_group_state: ConsumerGroupState = cgr_0_group.state  # 5 - EMPTY
cgr_0_group_is_simple:bool = cgr_0_group.is_simple_consumer_group




item = cgr_0_group_is_simple
pprint(item)
print("TYPE: ", type(item))
pprint(dir(item))


a.poll(10)