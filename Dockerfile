FROM python:alpine

WORKDIR /wiki

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

USER nobody

# This is isn't recommended, but it's enough to run a low-traffic wiki
# NB Flask defaults to looking for app.py
ENTRYPOINT flask run --host=0.0.0.0
