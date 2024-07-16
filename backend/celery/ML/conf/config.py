import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

HF_TOKEN = os.getenv('HF_TOKEN')
