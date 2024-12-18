FROM python:3.11
RUN pip install --upgrade pip && \
pip install wtforms==2.3.3 && \
    pip install 'apache-airflow[postgres]==2.10.0' && \
    # pip install 'apache-airflow[spark]==2.10.0' && \
    pip install dbt-postgres==1.5.9 && \
    pip install SQLAlchemy==1.4.49 && \
    pip install astronomer-cosmos && \
    pip install dag-factory && \
    pip install requests sqlalchemy psycopg2-binary pandas

#AWS specifics
RUN pip install boto3 && \
    pip install botocore && \
    pip install paramiko

#Adds support for HOCON files
RUN pip install pyhocon

RUN mkdir /project
COPY scripts/ /project/scripts/

RUN chmod +x /project/scripts/init.sh

ENTRYPOINT [ "/project/scripts/init.sh" ]