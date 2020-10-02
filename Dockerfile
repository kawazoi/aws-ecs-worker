FROM python:3.7
LABEL maintainer="lucas@lexter.ai"

ENV API_NAME=my-worker
WORKDIR /app

COPY worker/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ARG GIT_TOKEN
ARG LEXTER_DATA_VERSION=master
# RUN pip install git+https://${GIT_TOKEN}@github.com/lexter-ai/lexter-data.git@${LEXTER_DATA_VERSION}

RUN apt-get update
RUN apt-get install gettext -y

COPY .config.template .
RUN mkdir ~/.aws/
RUN envsubst < /app/.config.template > ~/.aws/config
RUN rm /app/.config.template
COPY . /app

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "worker/run_worker.py"]
