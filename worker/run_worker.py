import asyncio
import concurrent.futures
import functools  # at the top with the other imports
import logging
import sys

import settings
from core import config as cfg
from libs.my_task import MyTask


logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT)
logger = logging.getLogger(__name__)

NO_RESPONSE_FROM_SQS_MSG = "Failed to pool messages from queue. (queue: {})"
NO_MESSAGES_MSG = "No messages pooled. Waiting {} second(s) to try again."
ERROR_PROCESSING_MESSAGES_MSG = "Failed to process messages."


async def main():
    config = cfg.ConfigManager(echo=True)
    # settings.init_resources()
    settings.init_sqs_client_and_s3_bucket()
    logger.info(config.sqs)

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
            retry_cd = config.sqs["RETRY_COOLDOWN_SECONDS"]
            logger.info(NO_MESSAGES_MSG.format(retry_cd))
            await asyncio.sleep(retry_cd)

        else:
            msgs = resp["Messages"]

            for msg in msgs:
                try:
                    print(msg)
                    task_func_partial = functools.partial(MyTask.run, msg)
                    with concurrent.futures.ProcessPoolExecutor() as pool:
                        await loop.run_in_executor(pool, task_func_partial)

                except Exception as e:
                    logger.error(ERROR_PROCESSING_MESSAGES_MSG)
                    logger.error(e)


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("python `{}` starting...".format(sys.argv[0]))
    asyncio.run(main())
