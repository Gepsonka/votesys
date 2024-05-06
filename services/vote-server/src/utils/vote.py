import random
from .ring import Ring
from Crypto.PublicKey import RSA
from utils.constants import RING_SIZE


def fetch_random_voters(cursor, count: int):
    return cursor.execute(
        "SELECT * FROM Voter ORDER BY RANDOM() LIMIT ?", (count,)
    ).fetchall()


def calculate_signautre(private_keys, message: str):
    # shuffle list so that the order of the public keys is not known
    random.shuffle(private_keys)
    ring = Ring(private_keys)
    for i in range(len(private_keys)):
        sig = ring.sign_message(message, i)

    return sig, private_keys


def get_voter_by_id(cursor, voter_id: str):
    voter = cursor.execute(
        "SELECT * FROM Voter WHERE idNumber=?", (voter_id,)
    ).fetchone()
    # check if voter with id exists
    if voter is None:
        raise ValueError("Voter with id does not exist")

    return voter
    
def has_voter_already_voted(cursor, voter_id: str):
    voter = cursor.execute(
        "SELECT * FROM Voter WHERE idNumber=?", (voter_id,)
    ).fetchone()
    if voter is None:
        raise ValueError("Voter with id does not exist")
    
    return voter[-1]
    


def convert_keys_into_RsaKey_objects(private_keys):
    return [RSA.importKey(n) for n in private_keys]


def submit_vote(db, public_keys, signature, message):
    exported_public_keys = [key.export_key().decode("utf-8") for key in public_keys]
    signtature_str = [str(sig) for sig in signature]

    # Add vote to database
    db.cursor.execute(
        "INSERT INTO vote (vote, RSA_signature1, RSA_signature2, RSA_signature3, RSA_signature4, RSA_signature5, RSA_signature6, signer1_public_RSA_key, signer2_public_RSA_key, signer3_public_RSA_key, signer4_public_RSA_key, signer5_public_RSA_key) VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?,?,?)",
        (
            message,
            signtature_str[0],
            signtature_str[1],
            signtature_str[2],
            signtature_str[3],
            signtature_str[4],
            signtature_str[5],
            exported_public_keys[0],
            exported_public_keys[1],
            exported_public_keys[2],
            exported_public_keys[3],
            exported_public_keys[4],
        ),
    )
    db.conn.commit()

def get_vote_count(db):
    votes = db.cursor.execute("SELECT vote, COUNT(*) FROM vote GROUP BY vote").fetchall()
    vote_dict = {}
    for vote in votes:
        vote_dict[vote[0]] = vote[1]

    return vote_dict
    


def voter_voted(db, voter_id):
    db.cursor.execute("UPDATE Voter SET voted = 1 WHERE idNumber=?", (voter_id,))
    db.conn.commit()


def verify_vote(db, voteId):
    vote = db.cursor.execute("SELECT * FROM vote WHERE id=?", (voteId,)).fetchone()

    if vote is None:
        return None

    public_keys = [RSA.importKey(key) for key in vote[7:12]]
    signature = [int(sig) for sig in vote[1:7]]

    ring = Ring(public_keys)
    return ring.verify_message(vote[1], signature, public_keys, RING_SIZE)
