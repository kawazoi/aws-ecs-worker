import argparse
import asyncio
import boto3
import json
import logging

from dotenv import load_dotenv
from multiprocessing.pool import ThreadPool
from os import getenv


load_dotenv()
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


async def produce(args: dict):
    items = await _get_items()
    logging.info("Len items: {}".format(len(items)))

    pool = ThreadPool(int(args.max_threads))
    res = pool.map(_enqueue, items)
    pool.close()
    pool.join()

    logging.info(f"Enqueued {len(res)} item(s).")


async def _get_items() -> list:
    items = [
        {"contract_id": 1, "contract_type": "type_1", "text": "Hello world from SP"},
        {"contract_id": 2, "contract_type": "type_2", "text": "Hello world from RJ"},
        {"contract_id": 3, "contract_type": "type_3", "text": "Hello world from MG"},
    ]
    return items


def _enqueue(item):
    response = sqs.send_message(
        QueueUrl=getenv("SQS_QUEUE_URL"),
        DelaySeconds=int(getenv("SQS_DELAY_SECONDS")),
        MessageAttributes={
            "contract_id": {
                "DataType": "Number",
                "StringValue": str(item["contract_id"]),
            },
            "computation_nature": {"DataType": "String", "StringValue": "cpu_bound"},
        },
        MessageBody=json.dumps(item),
    )
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-max-threads", help="Número máximo de threads.", default=10)
    args = parser.parse_args()

    session = boto3.Session()
    sqs = session.client("sqs")

    asyncio.run(produce(args))
