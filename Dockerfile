FROM python:3.11-slim
WORKDIR /app

COPY . .

RUN mkdir local_save
RUN mkdir waveform_local

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]