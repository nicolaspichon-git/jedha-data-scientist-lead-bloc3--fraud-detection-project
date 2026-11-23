# The real-time producer, built on python:3.11-slim rather than on
# jedha/real-time-payments-api-lead-program, the base of the original
# Dockerfile (kept in _old/).
#
# Block: B3.
# Covers: B3-EC27.
#
# app.py is the vendor's, unchanged: this file only says how to run it. The
# Jedha base image is not pulled at all -- nothing says what it holds or
# whether it is still published -- so its dependencies are declared here.
#
# 3.11 to match the Airflow image.
FROM python:3.11-slim

WORKDIR /home/app

# What app.py imports: FastAPI served by gunicorn with uvicorn workers,
# slowapi for the rate limit, pandas to read the corpus, jinja2 for the
# templates. Pinned loosely, like the Airflow image.
RUN pip install --no-cache-dir \
        "fastapi>=0.110" \
        "uvicorn[standard]>=0.27" \
        "gunicorn>=21.2" \
        "slowapi>=0.1.9" \
        "pandas>=2.0" \
        "jinja2>=3.1"

COPY app.py .
COPY static ./static
COPY templates ./templates

# A non-root user: the service is reachable over HTTP and needs no privilege.
RUN useradd --create-home --uid 10001 producer && chown -R producer /home/app
USER producer

ENV PORT=4000
CMD ["sh", "-c", "exec gunicorn app:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker --workers 1"]
