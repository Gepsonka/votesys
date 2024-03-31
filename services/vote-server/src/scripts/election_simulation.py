import random
from utils.db import DB
import utils.vote as vote
import utils.constants as constants
from utils.ring import Ring
from Crypto.PublicKey import RSA
import json


class ElectionSimulation(object):
    def __init__(
        self,
        vote_distribution: float,
        voting_participation_rate: float = 63.7,
    ):
        self.database = DB("../votesys.db")
        self.voting_participation_rate = voting_participation_rate
        self.voted_for_winner_rate = vote_distribution
        self.winner_party = self._get_random_winner_party()

    def _get_random_winner_party(self):
        return random.choice(["DEM", "REP"])

    def _get_loser_party(self):
        if self.winner_party == "DEM":
            return "REP"
        return "DEM"

    def _voter_votes(self):
        """The 2020 US election had a voter participation rate of 63.7%.
        The sim follows this distribution if it is not specifies otherwise"""
        random_num = random.random()
        if random_num <= self.voting_participation_rate / 100:
            return True

        return False

    def _voter_voted_for_winner(self):
        random_num = random.random() / 100
        if random_num < 0.5:
            return False

        return True

    def _simulate_vote(self, voter, random_signers):
        if self._voter_voted_for_winner():
            voted_for_party = self.winner_party
        else:
            voted_for_party = self._get_loser_party()

        RSA_keys = vote.convert_keys_into_RsaKey_objects(
            [random_voter[6] for random_voter in random_signers] + [voter[6]],
        )

        signature, _ = vote.calculate_signautre(RSA_keys, voted_for_party)

        public_keys = [key.publickey() for key in RSA_keys]

        vote.submit_vote(
            self.database,
            public_keys,
            signature,
            voted_for_party,
        )

    def _verify_vote(self, vote):
        signatures = [int(sig) for sig in vote[2:8]]
        public_keys = [RSA.importkey(pk) for pk in vote[8:]]

        ring = Ring(public_keys)
        return ring.verify_message(
            vote[1], signatures, public_keys, constants.RING_SIZE
        )

    def simulate_election(self):
        voters = self.database.cursor.execute("SELECT * FROM Voter").fetchall()
        for voter in voters:
            random_voters = vote.fetch_random_voters(
                self.database.cursor, constants.RING_SIZE
            )
            if self._voter_votes():
                self._simulate_vote(voter, random_voters)

        del self.database

    def verify_votes(self):
        votes = self.database.cursor.execute("SELECT * FROM Vote").fetchall()
        for vote in votes:
            if self._verify_vote(vote):
                print("Vote verified: ", vote[1])
            else:
                print("Vote not valid: ", vote[1])


class CreateElectionResultReport(object):
    def __init__(self):
        self.database = DB("../votesys.db")

    def _get_vote_count(self):
        return self.database.cursor.execute("SELECT count(*) FROM Vote").fetchone()[0]

    def _get_voter_count(self):
        return self.database.cursor.execute("SELECT count(*) FROM Voter").fetchone()[0]

    def _classify_votes(self):
        return {
            "DEM": self.database.cursor.execute(
                "select count(*) from Vote where vote='DEM'"
            ).fetchone()[0],
            "REP": self.database.cursor.execute(
                "select count(*) from Vote where vote='REP'"
            ).fetchone()[0],
        }

    def _get_voting_participation_rate(self):
        return self._get_vote_count() / self._get_voter_count() * 100

    def _get_election_results(self):
        return {
            "DEM": self._classify_votes()["DEM"] / self._get_vote_count() * 100,
            "REP": self._classify_votes()["REP"] / self._get_vote_count() * 100,
        }

    def create_report(self):
        report = {
            "voter_count": self._get_voter_count(),
            "vote_count": self._get_vote_count(),
            "voting_participation_rate": self._get_voting_participation_rate(),
            "election_results": self._get_election_results(),
        }

        with open("../../election_results.json", "w") as file:
            json.dump(report, file, indent=4)

        del self.database
