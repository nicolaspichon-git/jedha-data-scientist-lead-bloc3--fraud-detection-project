import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import pandas as pd
from datetime import datetime
import io
import os
import random
import urllib.request


# THE CORPUS IS READ FROM THE DISK, NOT FROM S3 AT EVERY CALL (change of
# 2026-11-23, project BC03; the original is kept in _old/app.py). The original
# downloaded the whole of fraudTest.csv on every request to keep about one row
# in a thousand: about a minute per call, past gunicorn's 30-second worker
# timeout, so most calls ended with the worker killed.
#
# The file is now kept in a CACHE (a volume, see docker-compose.yml) and
# downloaded only when the cache is empty, at start-up; it is then indexed
# once, and each call reads ONE line at a random offset. gunicorn loads this
# module with --preload, in the master process, so a first download of about
# a minute does not run into the worker timeout.
#
# The draw is the same: the original kept each row with probability p, then
# sampled one of the rows kept -- a uniform draw over the file, which is what
# random.choice over the line offsets is.
SOURCE = os.environ.get("PRODUCER_SOURCE", "https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv")
CORPUS = os.environ.get("PRODUCER_CORPUS", "/home/app/data/fraudTest.csv")

# THE RATE LIMIT, per client address. "5/minute" is what the original declares,
# and stays the default. But its limiter is a FIXED window of 60 s opened by the
# first call: dag_ingest makes its five calls in a burst once a minute, and a
# burst that starts a few tenths of a second before the previous window closes
# is refused whole -- one run in two failed on 429 (2026-11-23).
# docker-compose.yml sets twice the client's cadence, so two consecutive bursts
# always fit in one window.
RATE_LIMIT = os.environ.get("PRODUCER_RATE_LIMIT", "5/minute")


def _fill_cache(source, path):
    """Download the corpus if the cache does not hold it yet.

    Written under a temporary name and renamed: a download cut short leaves a
    .part file, never a truncated corpus that the next start would trust.
    """
    if os.path.isfile(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    partial = path + ".part"
    print("corpus absent du cache : telechargement de %s" % source, flush=True)
    urllib.request.urlretrieve(source, partial)
    os.replace(partial, path)
    print("corpus en cache : %s (%d octets)" % (path, os.path.getsize(path)), flush=True)


def _index(path):
    """The header, and the byte offset of every data line."""
    offsets = []
    with open(path, "rb") as f:
        header = f.readline()
        position = f.tell()
        for line in f:
            offsets.append(position)
            position += len(line)
    return header.decode("utf-8"), offsets


_fill_cache(SOURCE, CORPUS)
HEADER, OFFSETS = _index(CORPUS)


def one_row():
    """One row of the corpus, drawn uniformly, as a one-line DataFrame."""
    with open(CORPUS, "rb") as f:
        f.seek(random.choice(OFFSETS))
        line = f.readline().decode("utf-8")
    return pd.read_csv(io.StringIO(HEADER + line), header=0, index_col=[0])


description = """
Welcome to Fraud Detection's real-time payments API. Try it out.
## Endpoints

There is currently just a few endpoints:

* `/`: **GET** request that display a simple default message.
* `/current-transactions`: **GET** request that gives you 1 current transaction

The API is limited to **5 calls/ minutes** 🚧. If you try more, your endpoint will throw back an error.
"""

app = FastAPI(
    title="Fraud Detection : Real-time Payments Producer",
    description=description,
    version="0.1",
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Starlette's current signature: the request FIRST, then the template's
    # name. The original's TemplateResponse("index.html", {"request": request})
    # is the old one, removed since; Starlette took the dict for the name and
    # "/" answered 500 (unhashable type: 'dict'), 2026-11-23.
    return templates.TemplateResponse(request, "index.html")

@app.get("/current-transactions")
@limiter.limit(RATE_LIMIT)
async def current_transactions(request: Request):
    """
    Return one current transaction in [`.to_json(orient="split")`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html) format in Pandas.
    """
    df = one_row()
    df = df.loc[:, ~df.columns.isin(["trans_date_trans_time", "fraud", "unix_time"])]
    df["current_time"]= datetime.now()
    return df.to_json(orient="split")

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000) 