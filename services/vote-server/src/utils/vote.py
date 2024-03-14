from .ring import Ring
from Crypto.PublicKey import RSA


def fetch_random_voters(cursor, count: int):
    return cursor.execute(
        "SELECT * FROM Voter ORDER BY RANDOM() LIMIT ?", (count,)
    ).fetchall()


def calculate_signautre(public_keys: str, message: str):
    ring = Ring(public_keys)
    for i in range(len(public_keys)):
        sig = ring.sign_message(message, i)

    return {"signature": sig, "public_keys": public_keys}


def get_voter_by_id(cursor, voter_id: str):
    voter = cursor.execute(
        "SELECT * FROM Voter WHERE idNumber=?", (voter_id,)
    ).fetchone()
    # check if voter with id exists
    if voter is None:
        raise ValueError("Voter with id does not exist")

    return voter


def convert_keys_into_RsaKey_objects(private_keys):
    return [RSA.importKey(n) for n in private_keys]
