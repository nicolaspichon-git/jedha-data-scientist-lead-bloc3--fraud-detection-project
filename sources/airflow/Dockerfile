FROM apache/airflow:2.10.4-python3.11

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Le paquet fraud/ est monte en editable : la logique est importable par les
# DAG comme par pytest, et un changement n'exige pas de reconstruire l'image.
