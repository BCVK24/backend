FROM python:3.11-slim
WORKDIR /app

COPY . .

RUN mkdir logs
RUN touch logs/error.log

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
