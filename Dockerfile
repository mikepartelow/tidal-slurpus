FROM debian

RUN apt-get update -yq && \
    apt-get install -yq curl python3 python3-pip gron jq


USER root
ENV PATH=/root/.local/bin:$PATH

RUN pip install tidalapi black pylint flake8

WORKDIR /app

CMD python3 ./dumpus.py
