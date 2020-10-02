#!/bin/sh
python -m nltk.downloader rslp
python /app/install_resources.py

exec "$@"
