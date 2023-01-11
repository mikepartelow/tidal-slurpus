FROM debian

RUN apt-get update -yq && \
    apt-get install -yq curl python3 python3-pip gron jq less


USER root
ENV PATH=/root/.local/bin:$PATH

RUN pip install tidalapi black pylint flake8

WORKDIR /app

RUN echo 'export PS1="[\u]:[\w] # "' >> /root/.bashrc

CMD python3 ./dumpus.py
