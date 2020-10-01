# pylint: disable=invalid-name
from pathlib import Path
import boto3
import csv
import json
import spacy

from letrusnlp.marker import LetrusMarker
from letrusnlp.settings import DEFAULT_PATHS
from letrusnlp.resources import LetrusResources

from core import config as cfg


config = cfg.ConfigManager(echo=False)

lr = LetrusResources()

COH_METRIX_DIR = DEFAULT_PATHS["RESOURCES"] / "coh_metrix"
ENEM_OPTIMAL_FILE = COH_METRIX_DIR / "coh-enem-optimal.csv"
MRC_WORDS_FILE = COH_METRIX_DIR / "MRC_psycholinguistics_words.json"

TMP_OUTPUT_DIR = Path("/tmp/coh-metrix-worker/csv")

MRC_PT_WORDS = dict()


def init_resources(overwrite=False):
    """
    Initializes global variables.
    """
    init_nlp_marker()
    load_coh_metrix_resources()
    initialize_enem_optimal()
    initialize_MRC_words()


def init_nlp_marker():
    global nlp_marker
    nlp = spacy.load(config.spacy["SPACY_MODEL_NAME"])
    nlp_marker = LetrusMarker(
        nlp,
        marker_categories=["pontos", "virgulas", "oralidades", "conectivos"],
    )

def init_sqs_client_and_s3_bucket():
    global sqs_client
    global s3_bucket
    session = boto3.Session()
    sqs_client = session.client("sqs")

    s3 = boto3.resource("s3")
    s3_bucket = s3.Bucket(config.s3["BUCKET"])


def initialize_enem_optimal():
    global enem_optimal
    with open(ENEM_OPTIMAL_FILE) as csvfile:
        reader = csv.reader(csvfile)
        enem_optimal = {
            row[1]: (float(row[2]), float(row[3]))
            for row in reader
            if row[2] and row[3]
        }


def initialize_MRC_words():
    with open(str(MRC_WORDS_FILE)) as f:
        data = json.load(f)
    for item in data:
        word = "%s_%s" % (item["translatedText"], item["category"])
        MRC_PT_WORDS[word] = item["score"]


def load_coh_metrix_resources():
    """Example of loading a resource using LetrusResource."""
    global FREQUENCIES
    lr.sync_resource_type_from_s3("coh_metrix")
    frequencies_path = COH_METRIX_DIR / "wl_cb_full_1gram_sketchengine.txt"
    FREQUENCIES = _load_frequencies(frequencies_path)


def _load_frequencies(path: Path):
    freq_count = {}
    corpus_size = 0

    with open(path, "r") as f:
        for line in f.readlines():
            if line.strip():
                token, count = line.strip().split("\t")
                freq_count[token] = int(count)
                corpus_size += int(count)

    freq_perc = {}
    for token in freq_count:
        freq_perc[token] = freq_count[token] / float(corpus_size)

    return freq_perc
