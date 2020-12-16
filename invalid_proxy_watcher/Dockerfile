FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir /invalid_proxy_watcher
WORKDIR /invalid_proxy_watcher
ADD requirements.txt /invalid_proxy_watcher/
RUN pip install -r requirements.txt
ADD . /invalid_proxy_watcher/