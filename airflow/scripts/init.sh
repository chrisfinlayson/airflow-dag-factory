#!/usr/bin/env bash

# Setup environment variables
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
export AIRFLOW__CORE__FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
export AIRFLOW__WEBSERVER__SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(16))")

DBT_POSTGRESQL_CONN="postgresql://${DBT_POSTGRES_USER}:${DBT_POSTGRES_PASSWORD}@${DBT_POSTGRES_HOST}:${POSTGRES_PORT}/${DBT_POSTGRES_DB}"

cd /dbt && dbt compile
rm -f /airflow/airflow-webserver.pid

# Wait for PostgreSQL to be ready with increased timeout
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if nc -z ${POSTGRES_HOST} ${POSTGRES_PORT}; then
        echo "PostgreSQL is ready!"
        break
    fi
    echo "Waiting for PostgreSQL... $i/30"
    sleep 2
done

# Initialize the database with verification
echo "Initializing Airflow database..."
airflow db init
sleep 5  # Give some time for initialization to complete

# Verify database initialization
echo "Verifying database initialization..."
airflow db check

# Create admin user with increased delay between retries
echo "Creating admin user..."
for i in {1..5}; do
    airflow users create \
        --username airflow_admin \
        --firstname admin \
        --lastname admin \
        --role Admin \
        --email admin2 \
        --password admin && break
    echo "Retry $i: Waiting before next attempt..."
    sleep 10
done

# Add connection
echo "Adding DBT connection..."
airflow connections add 'dbt_postgres_instance_raw_data' --conn-uri "$DBT_POSTGRESQL_CONN" || true

# Start services with delay between them
echo "Starting Airflow services..."
airflow scheduler &
sleep 10  # Give scheduler time to start
airflow webserver