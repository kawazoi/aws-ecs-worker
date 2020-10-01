import json
import logging
import spacy
import csv

from multiprocessing.pool import ThreadPool

from coh_metrix import metrics
from core import config as cfg
from core.abstract_task import AbstractTask
import settings


logging.basicConfig(level=cfg.LOG_LEVEL, format=cfg.LOG_FORMAT)
logger = logging.getLogger(__name__)


config = cfg.ConfigManager()


COMPONENTS_MAP = {
    "descriptive": metrics.Descriptive,
    "word_information": metrics.WordInformation,
    "lexical_diversity": metrics.LexicalDiversity,
    "syntactic_complexity": metrics.SyntacticComplexity,
    "connectives": metrics.Connectives,
    "readability": metrics.Readability,
    "intelligibility": metrics.Intelligibility,
}


START_PROCESSING_MSG = "Processing message {} (composition_id: {})"
MESSAGE_PROCESSED_MSG = "Processed message {} (composition_id: {})"
MESSAGE_PROCESSING_FAILED_MSG = "Failed to process message {} (composition_id: {}"


class MyTask(AbstractTask):
    """Tasks have two static methods to be overloaded.

    Don't use instance methods for processing tasks as the process will be run on a process pool,
    the original reference to the object would be on the parent process.

    They're static and should be self contained.

    """

    @staticmethod
    def run(msg):
        msg_id, contract_id, text, categories = parse_msg(msg)
        logger.info(START_PROCESSING_MSG.format(msg_id, composition_id))

        if not text:
            return dict()

        nlp, components = make_nlp_pipe_and_components(categories)

        doc = nlp(text)

        result = {}
        for component in components:
            result.update(component.to_json(doc))

        result = flatten_label_values(result)

        if result:
            upload_results_using_multithreading(result, composition_id)
            settings.sqs_client.delete_message(
                QueueUrl=config.sqs["QUEUE_URL"], ReceiptHandle=msg["ReceiptHandle"]
            )
            logger.info(MESSAGE_PROCESSED_MSG.format(msg_id, composition_id))
        else:
            logger.error(MESSAGE_PROCESSING_FAILED_MSG.format(msg_id, composition_id))


def parse_msg(msg):
    msg_id = msg["MessageId"]
    msg_body = json.loads(msg["Body"])
    composition_id = msg_body["id"]
    text = msg_body["composition_raw"]
    categories = msg_body["categories"]
    return msg_id, composition_id, text, categories


def make_nlp_pipe_and_components(categories: dict):
    nlp = load_nlp_with_marker()
    nlp = remove_components(nlp, list(COMPONENTS_MAP.keys()))
    if not categories:
        categories = {ctg: [] for ctg in list(COMPONENTS_MAP.keys())}
    components = []
    for ctg, _metrics in categories.items():
        try:
            component = COMPONENTS_MAP[ctg](nlp, **{ctg: _metrics})
            nlp.add_pipe(component, name=ctg, last=True)
            components.append(component)
        except KeyError:
            logging.error(
                'Category "%s" does not exist or has not yet been implemented.' % ctg
            )
    return nlp, components


def load_nlp_with_marker():
    nlp = spacy.load(config.spacy["SPACY_MODEL_NAME"])
    if nlp.has_pipe("marker"):
        nlp.remove_pipe("marker")
    nlp.add_pipe(settings.nlp_marker, name="marker", last=True)
    return nlp


def remove_components(nlp, components_to_remove):
    for pipe in components_to_remove:
        if nlp.has_pipe(pipe):
            nlp.remove_pipe(pipe)
    return nlp


def flatten_label_values(coh_metrix_output: dict) -> list:
    label_values = {}
    for cat, labels in coh_metrix_output.items():
        for label in labels:
            label_values[label["label"]] = label["value"]
    return label_values


def upload_results_using_multithreading(result, composition_id):
    list_of_inputs = []
    for label, value in result.items():
        csv_row = [composition_id, value]
        inputs = composition_id, label, csv_row
        list_of_inputs.append(inputs)

    # IO bound task > Use ThreadPool
    pool = ThreadPool(5)
    pool.map(export_and_upload_to_s3, list_of_inputs)
    pool.close()
    pool.join()


def export_and_upload_to_s3(inputs: tuple):
    composition_id, label, csv_row = inputs

    l_path = settings.TMP_OUTPUT_DIR / "{}/{}.csv".format(label, composition_id)
    l_path.parent.mkdir(exist_ok=True, parents=True)
    with open(l_path, "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(csv_row)

    s3_full_path = "{}/label={}/{}.csv".format(
        config.s3["BUCKET_LOCATION"], label, composition_id
    )
    settings.s3_bucket.upload_file(str(l_path), s3_full_path)
    logger.debug("uploaded {} to {}".format(l_path, s3_full_path))
