"""
Secret sharing scheme.
"""

from typing import List
from Crypto.Util import number

import random

from expression import Secret

p = number.getPrime(1024)

class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, bn: int): # expr is a scalar or a secret
        self.bn = bn
       
    def __repr__(self):
        # Helps with debugging.
        return self.bn

    def __add__(self, other):
        return Share(self.bn + other.bn % p)
        

    def __sub__(self, other):
        return Share(self.bn - other.bn % p)

    def __mul__(self, other):
        raise NotImplementedError("You need to implement this method.")


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    shares = list()
    s_sum = 0
    for i in range(num_shares - 1) :
        s_i = random.randint(range(p))
        share_i = Share(s_i)
        shares.append(share_i)
        s_sum += s_i % p
    share_0 = Share(secret - s_sum)
    shares.insert(0,share_0)
    return shares


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    secret = 0
    for s in shares : 
        secret += s.bn % p


# Feel free to add as many methods as you want.
