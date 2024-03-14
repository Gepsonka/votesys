from flask import Blueprint
from utils.constants import (
    US_STATES,
    RSA_KEY_SIZE,
    US_POPULATION_AGE_MEAN,
    US_POPULATION_AGE_STD,
    DB_PATH,
)
import random
import requests
from Crypto.PublicKey import RSA
from utils.population import truncated_normal
import sqlite3
import os

dummy_data_fill = Blueprint("dummy_data_fill", __name__)


@dummy_data_fill.route("/fill")
def fill():
    """Fill up database with random voters (10000).
    Utilizing batching (only uploading 100 at a time)"""

    voters = [{} for i in range(10)]
    age_samples = truncated_normal(
        18, 120, US_POPULATION_AGE_MEAN, US_POPULATION_AGE_STD
    )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for i in range(1000):
        for j in range(10):
            rsa_key = RSA.generate(RSA_KEY_SIZE, os.urandom)
            response = requests.get("https://api.namefake.com/english-united-states")
            res_data = response.json()
            voters[j]["name"] = res_data["name"]
            voters[j]["age"] = age_samples[j]

            print(voters[j]["age"])

            if "female" in res_data["url"]:
                voters[j]["sex"] = "female"
            else:
                voters[j]["sex"] = "male"

            voters[j]["state"] = US_STATES[random.randint(0, 49)]
            voters[j]["idNumber"] = "".join(
                [str(random.randint(0, 9)) for _ in range(15)]
            )

            voters[j]["privateKeyRSA"] = (
                rsa_key.publickey().export_key().decode("utf-8")
            )
            voters[j]["publicKeyRSA"] = rsa_key.export_key().decode("utf-8")

        cursor.executemany(
            """
                INSERT INTO voter (idNumber, name, sex, age, state, publicKeyRSA, privateKeyRSA)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    voter["idNumber"],
                    voter["name"],
                    voter["sex"],
                    voter["age"],
                    voter["state"],
                    voter["publicKeyRSA"],
                    voter["privateKeyRSA"],
                )
                for voter in voters
            ],
        )
        conn.commit()
        age_samples = truncated_normal(
            18, 120, US_POPULATION_AGE_MEAN, US_POPULATION_AGE_STD
        )

    cursor.close()

    return {"message": "Database filled with 10000 voters"}
