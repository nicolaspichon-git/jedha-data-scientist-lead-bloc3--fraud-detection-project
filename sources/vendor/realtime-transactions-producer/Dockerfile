# The real-time producer, built on python:3.11-slim rather than on
# jedha/real-time-payments-api-lead-program, the base of the original
# Dockerfile (kept in _old/).
#
# Block: B3.
# Covers: B3-EC27.
#
# The Jedha base image is not pulled at all -- nothing says what it holds or
# whether it is still published -- so its dependencies are declared here.
# app.py is the vendor's with ONE change, the corpus read from a local cache
# filled once (see its header; the original is in _old/app.py).
#
# 3.11 to match the Airflow image.
FROM python:3.11-slim

WORKDIR /home/app

# What app.py imports: FastAPI served by gunicorn with uvicorn workers,
# slowapi for the rate limit, pandas to read the corpus, jinja2 for the
# templates. Pinned loosely, like the Airflow image -- except pandas below 4:
# to_json() writes current_time in epoch milliseconds by default, the format
# fraud/stream.py reads, and pandas 4 announces it will switch to ISO.
RUN pip install --no-cache-dir \
        "fastapi>=0.110" \
        "uvicorn[standard]>=0.27" \
        "gunicorn>=21.2" \
        "slowapi>=0.1.9" \
        "pandas>=2.0,<4" \
        "jinja2>=3.1"

# THE CORPUS CACHE: an empty directory owned by the service's user, so the
# volume mounted on it (docker-compose.yml) is writable. app.py downloads the
# corpus into it at the first start, and never again while the volume lives.
RUN mkdir -p data

COPY app.py .
COPY static ./static
COPY templates ./templates

# A non-root user: the service is reachable over HTTP and needs no privilege.
RUN useradd --create-home --uid 10001 producer && chown -R producer /home/app
USER producer

ENV PORT=4000
# --preload: app.py is imported once, by the master, before the worker exists;
# the first download of the corpus then cannot trip the worker timeout.
CMD ["sh", "-c", "exec gunicorn app:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --workers 1 --preload"]
