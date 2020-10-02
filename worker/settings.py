import boto3

from core import config as cfg


config = cfg.ConfigManager(echo=False)


def init_sqs_client_and_s3_bucket():
    global sqs_client
    session = boto3.Session()
    sqs_client = session.client("sqs")
