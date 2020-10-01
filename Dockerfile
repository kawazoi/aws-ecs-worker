FROM python:3.7
LABEL maintainer="lucas@lexter.ai"

WORKDIR /app
RUN apt-get update
RUN apt-get install gettext -y

# Install awscli
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

# Install requirements
COPY 3_consumer/requirements.txt /app
RUN pip install numpy==1.19.1
RUN pip install -r requirements.txt

# Install letrusnlp
ARG GIT_TOKEN
ARG LETRUSNLP_VERSION=DEV_v1.1.8
RUN pip install -U git+https://${GIT_TOKEN}@github.com/letrustech/letrus-nlp.git@${LETRUSNLP_VERSION}
RUN python3 -m nltk.downloader wordnet
RUN python3 -m nltk.downloader omw

# Download resources
COPY scripts/ /app/scripts
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ARG SPACY_MODEL_NAME=pt_lexter_news_tagger_parser_sm
ARG SPACY_MODEL_VERSION=0.0.0
RUN python scripts/download_resources.py
RUN python scripts/install_spacy_model.py

COPY aws-config.template /app/aws-config.template
RUN mkdir ~/.aws/
RUN envsubst < /app/aws-config.template > ~/.aws/config
RUN rm /app/aws-config.template

COPY 3_consumer/ /app

CMD ["python", "run_consumer.py"]
