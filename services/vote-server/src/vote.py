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
def submit_vote():
    database = DB()
    data = request.json
    voter_id = data["voter_id"]
    try:
        voter = get_voter_by_id(database.cursor, voter_id)
        voter_private_key = voter[6]
        key = RSA.importKey(voter_private_key)
        print("Voter private key: ", key.d)
    except ValueError as e:
        return abort(404, description="Voter with id does not exist")

    random_voters = fetch_random_voters(database.cursor, 4)

    RSA_keys = convert_keys_into_RsaKey_objects(
        [str(random_voter[6]) for random_voter in random_voters]
        + [str(voter_private_key)]
    )

    public_keys = [key.publickey() for key in RSA_keys]

    if data["message"] == "DEM" or data["messsage"] == "REP":
        signature = calculate_signautre(public_keys, data["message"])
    else:
        return abort(400, description="Invalid message (possiblities are DEM/REP)")

    # shuffle list so that the order of the public keys is not known
    random.shuffle(public_keys)

    # Add vote to database
    database.cursor.execute(
        "INSERT INTO vote (vote, RSA_signature, signer1_public_RSA_key, signer2_public_RSA_key, signer3_public_RSA_key, signer4_public_RSA_key, signer5_public_RSA_key) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data["message"],
            signature,
            public_keys[0],
            public_keys[1],
            public_keys[2],
            public_keys[3],
            public_keys[4],
        ),
    )
    database.conn.commit()

    return {"status": "success"}
