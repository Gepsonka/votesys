from datetime import datetime
from flask import Flask, request
from fill_database_with_dummy_data import dummy_data_fill
from utils.constants import VOTE_TIME_INTERVAL

# to run : flask --app main run
app = Flask(__name__)
app.register_blueprint(dummy_data_fill)


@app.route("/voting-interval", methods=["GET"])
def voting_interval():
    return {
        "start": VOTE_TIME_INTERVAL[0].isoformat(),
        "end": VOTE_TIME_INTERVAL[1].isoformat(),
        "votingIsOpen": VOTE_TIME_INTERVAL[0] < datetime.now() < VOTE_TIME_INTERVAL[1],
    }


@app.route("/vote", methods=["POST"])
def vote():
    data = request.json

    return {"message": "Vote received"}
