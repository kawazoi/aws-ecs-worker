import json
import logging

from core import config as cfg
from core.abstract_task import AbstractTask
import settings


logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT)
logger = logging.getLogger(__name__)


config = cfg.ConfigManager()


START_PROCESSING_MSG = "Processing message {} (contract_id: {})"
MESSAGE_PROCESSED_MSG = "Processed message {} (contract_id: {})"
MESSAGE_PROCESSING_FAILED_MSG = "Failed to process message {} (contract_id: {}"


class MyTask(AbstractTask):
    """Tasks have two static methods to be overloaded.

    Don't use instance methods for processing tasks as the process will be run on a process pool,
    the original reference to the object would be on the parent process.

    They're static and should be self contained.
    """

    @staticmethod
    def run(msg):
        msg_id, contract_id, text, contract_type = parse_msg(msg)
        logger.info(START_PROCESSING_MSG.format(msg_id, contract_id))
        result = process_text(text, contract_type)
        if result:
            settings.sqs_client.delete_message(
                QueueUrl=config.sqs["QUEUE_URL"], ReceiptHandle=msg["ReceiptHandle"]
            )
            logger.info(MESSAGE_PROCESSED_MSG.format(msg_id, contract_id))
        else:
            logger.error(MESSAGE_PROCESSING_FAILED_MSG.format(msg_id, contract_id))


def parse_msg(msg):
    msg_id = msg["MessageId"]
    msg_body = json.loads(msg["Body"])
    contract_id = msg_body["contract_id"]
    contract_type = msg_body["contract_type"]
    text = msg_body["text"]
    return msg_id, contract_id, text, contract_type


def process_text(text: str, contract_type: str) -> dict:
    return {
        "markers": [
            {
                "parent_text_hash": "abc",
                "label": "label_1",
                "start": 1,
                "end": 2,
                "text": "marked text",
            }
        ]
    }
