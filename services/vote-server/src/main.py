from datetime import datetime
from flask import Flask, request
from flask_cors import CORS
from fill_database_with_dummy_data import dummy_data_fill
from utils.constants import VOTE_TIME_INTERVAL
from dotenv import load_dotenv
from vote import vote
from scripts.convert_rsa_keys_to_pem_format_db import convert_rsa_keys_to_pem_format_db


load_dotenv("../.env")

# to run : flask --app main run
app = Flask(__name__)
CORS(app)
app.register_blueprint(dummy_data_fill)
app.register_blueprint(vote, url_prefix="/vote")
