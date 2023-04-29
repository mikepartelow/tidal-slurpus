FROM debian

RUN apt-get update -yq && \
    apt-get install -yq curl python3 python3-pip gron jq less vim


USER root
ENV PATH=/root/.local/bin:$PATH

COPY app/patch-tidal.diff /tmp/patch-tidal.diff

RUN pip install tidalapi black pylint flake8 && \
    patch < /tmp/patch-tidal.diff /usr/local/lib/python3.9/dist-packages/tidalapi/user.py

WORKDIR /app

RUN echo 'export PS1="[\u]:[\w] # "' >> /root/.bashrc

CMD python3 ./dumpus.py
