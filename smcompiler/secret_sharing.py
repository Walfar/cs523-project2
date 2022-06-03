"""
Secret sharing scheme.
"""

import json
from typing import List

import random
import sympy

from expression import Secret

p = sympy.randprime(2**29, 2**32)

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
        return Share((self.bn + other.bn) % p)
        

    def __sub__(self, other):
        return Share((self.bn - other.bn) % p)

    def __mul__(self, other):
        return Share((self.bn * other.bn) % p)  


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    shares = list()
    s_sum = 0
    for i in range(num_shares - 1) :
        s_i = random.randint(0, p-1)
        share_i = Share(s_i)
        shares.append(share_i)
        s_sum += s_i % p
    num = (secret - s_sum) % p 
    share_0 = Share(num)
    shares.insert(0,share_0)
    return shares


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    secret = 0
    for s in shares : 
        secret += s.bn
    return secret % p  


# Feel free to add as many methods as you want.