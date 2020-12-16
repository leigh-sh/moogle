FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir /proxy_api
WORKDIR /proxy_api
ADD requirements.txt /proxy_api/
RUN pip install -r requirements.txt
ADD . /proxy_api/