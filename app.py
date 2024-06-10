from flask import Flask
from dotenv import load_dotenv
import os
import logging

load_dotenv()
app = Flask(__name__)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SHARED_SECRET = os.getenv('SHARED_SECRET')
S3_BUCKET = os.getenv('AWS_BUCKET_NAME')

import process_pdf
import pdf_to_image
