FROM python:2.7

RUN ["pip","install","flask"]

COPY server.py server.py
COPY wait-for-it.sh wait-for-it.sh
RUN chmod +x wait-for-it.sh 

ENTRYPOINT ["./wait-for-it.sh", "elasticsearch:9200" ,"--", "python", "server.py"]
