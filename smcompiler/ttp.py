"""
Trusted parameters generator.

MODIFY THIS FILE.
"""

from secret_sharing import p
import random
from typing import (
    Dict,
    Set,
    Tuple,
)

from communication import Communication
from secret_sharing import(
    share_secret,
    Share,
)

# Feel free to add as many imports as you want.


class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        self.participant_ids: Set[str] = set()
        self.dict = {}


    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        """     
        if op_id not in self.dict:
            a = random.randint(0, p-1)
            b = random.randint(0, p-1)
            c = (a * b) % p
            self.dict[op_id] = share_secret(a, len(self.participant_ids)), share_secret(b, len(self.participant_ids)), share_secret(c, len(self.participant_ids))
        a_shares, b_shares, c_shares = self.dict[op_id]
        return a_shares[list(self.participant_ids).index(client_id)], b_shares[list(self.participant_ids).index(client_id)], c_shares[list(self.participant_ids).index(client_id)]   

    # Feel free to add as many methods as you want.
