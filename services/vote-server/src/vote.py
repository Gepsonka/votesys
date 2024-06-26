import random
from flask import Blueprint, abort, request
import os
from utils.vote import *
from utils.db import DB
from Crypto.PublicKey import RSA

vote = Blueprint("vote", __name__)


@vote.route("/get-voting-interval", methods=["GET"])
def get_voting_time_interval():
    print("ide belépett")
    return {
        "vote_start": os.environ.get("VOTE_START"),
        "vote_end": os.environ.get("VOTE_END"),
    }


@vote.route("/get-votes", methods=["GET"])
def get_number_of_votes():
    database = DB()
    vote_dict = get_vote_count(database)

    del database
    return vote_dict, 200


@vote.route("/<voterId>", methods=["GET"])
def check_if_voter_exists(voterId):
    database = DB()
    voter = get_voter_by_id(database.cursor, voterId)
    print("itt van")
    print(voter)
    if voter is None:
        del database
        return {
            "code": "voter_id_not_found",
            "reason": "Voter with id does not exist",
        }, 404
    else:
        del database
        return {"status": "success"}, 200
        
@vote.route("/hasVoted/<voterId>", methods=["GET"])
def check_if_voter_has_already_voted(voterId):
    database = DB()
    already_voted = has_voter_already_voted(database.cursor, voterId)
    
    return str(already_voted == 1)


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
        return {
            "code": "voter_id_not_found",
            "message": "Voter with id does not exist",
        }, 404

    if voter[8] == 1:
        return {
            "code": "voter_already_voted",
            "message": "Voter has already voted",
        }, 400

    random_voters = fetch_random_voters(database.cursor, 4)

    RSA_keys = convert_keys_into_RsaKey_objects(
        [str(random_voter[6]) for random_voter in random_voters]
        + [str(voter_private_key)]
    )

    public_keys = [key.publickey() for key in RSA_keys]

    if data["message"] == "DEM" or data["message"] == "REP":
        signature, _ = calculate_signautre(RSA_keys, data["message"])
    else:
        return {
            "code": "invalid_message",
            "message": "Possible messages are 'DEM' or 'REP'",
        }, 400

    submit_vote(database, public_keys, signature, data["message"])

    voter_voted(database, voter_id)

    del database

    return {"status": "success"}
