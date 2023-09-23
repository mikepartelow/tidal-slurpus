FROM debian

RUN apt-get update -yq && \
    apt-get install -yq curl python3 python3-pip python3-venv gron jq less vim

USER root
ENV PATH=/root/.local/bin:$PATH

COPY app/patch-tidal.diff /tmp/patch-tidal.diff

RUN python3 -m venv /venv && \
    /venv/bin/pip install tidalapi black pylint flake8

# RUN patch < /tmp/patch-tidal.diff /venv/lib/python3.11/site-packages/tidalapi/user.py

WORKDIR /app

RUN echo 'export PS1="[\u]:[\w] # "' >> /root/.bashrc

CMD /venv/bin/python3 ./dumpus.py
