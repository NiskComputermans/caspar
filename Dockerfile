FROM python:latest
RUN mkdir /log
COPY app.py /src/
RUN mkdir /conf/
COPY libmwostat.py /src/
COPY requirements.txt /src/
COPY conf/caspar.conf /conf/
RUN pip install -r /src/requirements.txt
VOLUME /conf/
