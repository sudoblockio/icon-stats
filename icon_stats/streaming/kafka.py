from time import sleep
from typing import Any

from confluent_kafka import Consumer, KafkaError, Producer, TopicPartition
from confluent_kafka.admin import AdminClient

# from loguru import logger
from pydantic import BaseModel

from icon_stats.config import config
from icon_stats.log import logger


def get_current_offset(session):
    """
    For backfilling only, this function works with the init container to look up
    it's job_id so it can line that up with it's consumer group and offest so that
    we can backfill up to a given point and then kill the worker afterwards.
    """
    if config.JOB_ID is None:
        return config.CONSUMER_GROUP, None

    output = {}
    while True:
        logger.info(f"Getting kafka job with job_id = {config.JOB_ID}")
        sql = f"select * from kafka_jobs WHERE job_id='{config.JOB_ID}';"
        result = session.execute(sql).fetchall()
        session.commit()

        if len(result) == 0:
            logger.info(f"Did not find job_id={config.JOB_ID} - sleeping")
            sleep(2)
            continue

        for r in result:
            # Keyed on tuple of topic, partition to look up the stop_offset
            output[(r[2], r[3])] = r[4]

        return r[1], output


class KafkaClient(BaseModel):
    name: str = None
    sleep_seconds: float = 0.25
    session: Any = None
    kafka_server: str = config.KAFKA_BROKER_URL
    consumer_group: str = None
    topic: str = None
    msg_count: int = 0
    consumer: Any = None
    consumer_schema: Any = None
    consumer_deserializer: Any = None
    json_producer: Any = None
    partition_dict: dict = None
    protobuf_producer: Any = None
    protobuf_serializer: Any = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.name is None:
            self.name = self.topic

        self.consumer = Consumer(
            {
                "bootstrap.servers": self.kafka_server,
                "group.id": self.consumer_group,
                # "queued.max.messages.kbytes": "100MB",
                # Offset determined by worker type head (latest) or tail (earliest)
                "auto.offset.reset": config.CONSUMER_AUTO_OFFSET_RESET,
            }
        )

        # Producers
        # Json producer for dead letter queues
        self.json_producer = Producer({"bootstrap.servers": self.kafka_server})

        admin_client = AdminClient({"bootstrap.servers": self.kafka_server})
        topics = admin_client.list_topics().topics

        if self.topic and self.topic not in topics:
            raise RuntimeError()

        self.init()

    def start(self):
        self.consumer.subscribe([self.topic])
        logger.info("Kafka consumer connected...")

        while True:
            # Poll for a message
            msg = self.consumer.poll(timeout=1)

            # If no new message, try again
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    err_msg = "{topic} {partition} reached end at offset {offset}".format(
                        topic=msg.topic(),
                        partition=msg.partition(),
                        offset=msg.offset(),
                    )
                    logger.error("Kafka consumer: " + err_msg)
                if msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    logger.error(
                        f"Kafka consumer: Kafka topic {msg.topic()} not ready. Restarting."
                    )
                elif msg.error():
                    logger.error("Kafka consumer: " + str(msg.error()))
                sleep(1)
                continue
            else:
                self.msg_count += 1
                # For backfilling only
                self.handle_backfill_stop(msg)
                # value = msg.value()
                if self.msg_count % 10000 == 0:
                    logger.info(
                        f"msg count {self.msg_count} for consumer group " f"{self.consumer_group}"
                    )

                self.process(msg)

        # Flush the last of the messages
        self.json_producer.flush()

    def init(self):
        """Overridable process that runs on init."""
        pass

    def process(self, msg):
        """Overridable process that processes each message."""
        pass

    def get_offset_per_partition(self):
        topic = self.consumer.list_topics(topic=self.topic)
        partitions = [
            TopicPartition(self.topic, partition)
            for partition in list(topic.topics[self.topic].partitions.keys())
        ]

        return self.consumer.position(partitions)

    def handle_backfill_stop(self, msg):
        if self.partition_dict is not None:
            if self.msg_count % 1000 == 0:
                end_offset = self.partition_dict[(self.topic, msg.partition())]
                offset = [
                    i.offset
                    for i in self.get_offset_per_partition()
                    if i.partition == msg.partition() and i.topic == self.topic
                ][0]

                logger.info(f"offset={offset} and end={end_offset}")

                if offset > end_offset:
                    logger.info(f"Reached end of job at offset={offset} and end={end_offset}")
                    import sys

                    logger.info("Exiting.")
                    sys.exit(0)
