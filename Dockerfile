FROM bitnami/spark
COPY ./Main.py /
RUN pip install cassandra-driver



