from utils.db import DB
from Crypto.PublicKey import RSA
from utils.constants import RSA_KEY_SIZE
from OpenSSL.crypto import PKey, TYPE_RSA
import concurrent.futures


BATCH_SIZE = 100


def generate_RSA_key(*args, **kwargs):
    key = RSA.generate(RSA_KEY_SIZE)
    public_key = key.publickey().exportKey()
    private_key = key.exportKey()
    return public_key, private_key


def generate_RSA_keys(num_of_keys=1):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        keys = list(executor.map(generate_RSA_key, range(num_of_keys)))
    return keys


def replace_rsa_keys_in_db_in_batches(userIds):
    db = DB()
    keys = generate_RSA_keys(len(userIds))
    keys_with_user_ids = [
        (keys[i][0], keys[i][1], userIds[i]) for i in range(len(userIds))
    ]
    db.cursor.executemany(
        "UPDATE Voter SET publicKeyRSA = ?, privateKeyRSA = ? WHERE id = ?",
        keys_with_user_ids,
    )
    db.conn.commit()


def convert_rsa_keys_to_pem_format_db():
    db = DB()
    voter_count = db.cursor.execute("SELECT COUNT(*) FROM Voter").fetchone()[0]
    all_voters = db.cursor.execute("SELECT id FROM Voter").fetchall()
    print("fetched all voters from database")
    for i in range(0, len(all_voters), BATCH_SIZE):
        batch = all_voters[i : i + BATCH_SIZE]
        replace_rsa_keys_in_db_in_batches([voter[0] for voter in batch])
        print(f"RSA keys converted to PEM format for voter batch")
    print("RSA keys converted to PEM format in database")


if __name__ == "__main__":
    convert_rsa_keys_to_pem_format_db()
