FROM python:3.4

ADD requirements.txt /opt/twitter_example/

RUN pip install -r /opt/twitter_example/requirements.txt

COPY twitter_elastic.py /opt/twitter_example/

ENTRYPOINT ["python3","-u","/opt/twitter_example/twitter_elastic.py"]

CMD ["trump", "USA","Docker"]