import asyncio
import concurrent.futures
import functools  # at the top with the other imports
import logging
import sys

import settings
from core import config as cfg
from libs.coh_metrix_task import CohMetrixTask


logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT)
logger = logging.getLogger(__name__)


NO_RESPONSE_FROM_SQS_MSG = "Failed to pool messages from queue. (queue: {})"
NO_MESSAGES_MSG = ("No messages pooled. Waiting {} second(s) to try again.")
ERROR_PROCESSING_MESSAGES_MSG = "Failed to process messages."


async def main():
    config = cfg.ConfigManager(echo=True)
    settings.init_resources()
    settings.init_sqs_client_and_s3_bucket()

    loop = asyncio.get_running_loop()

    # Receive messages can get more than 1 message per iteration
    while True:
        resp = settings.sqs_client.receive_message(
            QueueUrl=config.sqs["QUEUE_URL"],
            MaxNumberOfMessages=config.sqs["BATCH_SIZE"],
        )

        if resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
            logger.error(NO_RESPONSE_FROM_SQS_MSG.format(config.sqs["QUEUE_URL"]))
            logger.error(resp)

        elif "Messages" not in resp:
            SLEEP_TIME = 1
            logger.info(NO_MESSAGES_MSG.format(config.sqs["QUEUE_URL"], SLEEP_TIME))
            await asyncio.sleep(SLEEP_TIME)

        else:
            msgs = resp["Messages"]

            for message in msgs:
                try:
                    task_func_partial = functools.partial(CohMetrixTask.run, message)
                    with concurrent.futures.ProcessPoolExecutor() as pool:
                        await loop.run_in_executor(pool, task_func_partial)

                except Exception as e:
                    logger.error(ERROR_PROCESSING_MESSAGES_MSG)
                    logger.error(e)


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("python `{}` starting...".format(sys.argv[0]))
    asyncio.run(main())
