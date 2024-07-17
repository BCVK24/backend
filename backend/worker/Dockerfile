FROM python:3.11-slim
WORKDIR /app

COPY . .

RUN pip install faststream
RUN pip install redis
RUN pip install sqlalchemy

CMD ["python3", "worker.py"]