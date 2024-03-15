import random
from flask import Blueprint, abort, request
from datetime import datetime
from utils.ring import Ring
import sqlite3
import os
from utils.constants import DB_PATH, RSA_KEY_SIZE
from utils.vote import (
    convert_keys_into_RsaKey_objects,
    fetch_random_voters,
    calculate_signautre,
    get_voter_by_id,
    submit_vote,
    voter_voted,
)
from utils.db import DB
from Crypto.PublicKey import RSA

vote = Blueprint("vote", __name__)


@vote.route("/get-voting-interval", methods=["GET"])
def get_voting_time_interval():
    return {
        "vote_start": os.environ.get("VOTE_START"),
        "vote_end": os.environ.get("VOTE_END"),
    }


@vote.route("/submit-vote", methods=["POST"])
def submit_vote_endpoint():
    database = DB()
    data = request.json
    voter_id = data["voter_id"]

    try:
        voter = get_voter_by_id(database.cursor, voter_id)
        print("voter: ", voter)
        voter_private_key = voter[6]
    except ValueError as e:
        return abort(404, description="Voter with id does not exist")

    if voter[8] == 1:
        return {
            "status": "failed",
            "reason": "Voter has already voted",
        }, 400

    random_voters = fetch_random_voters(database.cursor, 4)

    RSA_keys = convert_keys_into_RsaKey_objects(
        [str(random_voter[6]) for random_voter in random_voters]
        + [str(voter_private_key)]
    )

    public_keys = [key.publickey() for key in RSA_keys]

    # shuffle list so that the order of the public keys is not known
    random.shuffle(public_keys)

    if data["message"] == "DEM" or data["messsage"] == "REP":
        signature, _ = calculate_signautre(RSA_keys, data["message"])
    else:
        return abort(400, description="Invalid message (possiblities are DEM/REP)")

    submit_vote(database, public_keys, signature, data["message"])

    voter_voted(database, voter_id)

    del database

    return {"status": "success"}
