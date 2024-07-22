import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv('HF_TOKEN')
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=postgres
# DB_PASS=postgres
# DB_NAME=vk-pg
# CLIENT_SECRET=2aZ4EfVxb2GGvoWBPOwc
# HOST_ID=user531852925
