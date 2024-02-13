import json
from typing import Type

from icon_stats.config import config
from icon_stats.db import session_factory
from icon_stats.schemas.block_etl_pb2 import BlockETL, LogETL, TransactionETL
from icon_stats.streaming.kafka import KafkaClient, get_current_offset


class TransactionsWorker(KafkaClient):
    msg_count: int = 0

    block: Type[BlockETL] = BlockETL()
    transaction: Type[TransactionETL] = TransactionETL()
    log: Type[LogETL] = LogETL()

    def process_transaction(self):
        # Ignore any unsuccessful txs
        if self.transaction.status != "0x1":
            return

        # Ignore anything without a method call like contract creation events
        if self.transaction.data == "":
            return

        data = json.loads(self.transaction.data)

        if "method" not in data:
            return

        method = data["method"]

    def process(self, msg):
        # Deserialize msg
        self.block.ParseFromString(msg.value())

        for tx in self.block.transactions:
            if tx.to_address == config.governance_address:
                # Skip all Txs not to the gov address
                self.transaction = tx
                self.process_transaction()


def transactions_worker_head():
    with session_factory() as session:
        kafka = TransactionsWorker(
            session=session,
            topic=config.CONSUMER_TOPIC_BLOCKS,
            consumer_group=config.CONSUMER_GROUP + "-head",
        )

        kafka.start()


def transactions_worker_tail():
    with session_factory() as session:
        consumer_group, partition_dict = get_current_offset(session)

        kafka = TransactionsWorker(
            session=session,
            topic=config.CONSUMER_TOPIC_BLOCKS,
            consumer_group=consumer_group,
            partition_dict=partition_dict,
        )

        kafka.start()
