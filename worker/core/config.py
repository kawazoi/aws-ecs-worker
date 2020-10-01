import logging
import os
from typing import Optional, Any


DEBUG = bool(int(os.environ.get("DEBUG", "0")))
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"



class ConfigManager:
    """
    Use this class instead of making direct reference to env
    To centralize constants names and such.
    """

    def __init__(self, echo=False):
        self.echo = echo

    @property
    def sqs(self) -> dict:
        return dict(
            QUEUE_URL=self._fetch_from_env("SQS_QUEUE_URL"),
            DELAY_SECONDS=int(self._fetch_from_env("SQS_DELAY_SECONDS", 10)),
            MAX_RETRIES=int(self._fetch_from_env("SQS_MAX_WORKER_RETRIES", 1)),
            RETRY_COOLDOWN_SECONDS=int(
                self._fetch_from_env("SQS_RETRY_COOLDOWN_SECONDS", 30)
            ),
            BATCH_SIZE=int(self._fetch_from_env("SQS_BATCH_SIZE", 10)),
        )

    @property
    def s3(self) -> dict:
        return dict(
            BUCKET=self._fetch_from_env("S3_BUCKET"),
            BUCKET_LOCATION=self._fetch_from_env("S3_BUCKET_LOCATION"),
        )

    @property
    def spellchecker(self) -> dict:
        return dict(
            URL=self._fetch_from_env("SPELLCHECKER_URL"),
            TOKEN=self._fetch_from_env("SPELLCHECKER_TOKEN", ""),
        )

    @property
    def languagetool(self) -> dict:
        return dict(
            URL=self._fetch_from_env("LANGUAGETOOL_URL"),
            TOKEN=self._fetch_from_env("LANGUAGETOOL_TOKEN", ""),
        )

    @property
    def spacy(self) -> dict:
        return dict(
            SPACY_MODEL_NAME=self._fetch_from_env("SPACY_MODEL_NAME"),
            SPACY_MODEL_VERSION=self._fetch_from_env("SPACY_MODEL_VERSION", ""),
        )

    def _fetch_from_env(self, varname: str = "", default: Any = None) -> Optional[str]:
        """
        Tries to fetch a variable from the conf file, falls back to env var.

        :param varname: Name of the env var to fallback to
        :param default: If the value is not set, return default instead.
        :return The value, if found, otherwise default.
        """

        value = os.environ.get(varname, None)
        if not value:
            if self.echo:
                logging.warning("{} not found as environment var".format(varname))
        else:
            if default:
                value = default

        if value:
            if self.echo:
                logging.debug("{} found as environment variable".format(varname))
        elif default:
            value = default

        return value
