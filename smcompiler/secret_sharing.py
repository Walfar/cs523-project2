"""
Secret sharing scheme.
"""

from typing import List
from Crypto.Util import number

from smcompiler.expression import Expression, Secret
import random

class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, expr, beaver_triplets : tuple, p : int): # expr is a scalar or a secret
        self.expr = expr
       
    def __repr__(self):
        # Helps with debugging.
        return self.expr.__repr__

    def __add__(self, other):
        value = self.expr.value + other.expr.value % self.p
        

    def __sub__(self, other):
        return self.expr.value - other.expr.value % self.p 

    def __mul__(self, other):
        raise NotImplementedError("You need to implement this method.")


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    p = number.getPrime(1024)
    randomlist = random.sample(range(p), num_shares)
    shares = list()
    s_sum = 0
    for i in range(num_shares - 1 ) :
        s_i = random.randint(range(p))
        share_i = Share(Secret(s_i),None,p)
        shares.append(share_i)
        s_sum += s_i % p
    share_0 = Share(Secret(secret - s_sum),None,p)
    shares.insert(0,share_0)
    return shares


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    secret = 0
    for s in shares : 
        secret += s.value % s.p


# Feel free to add as many methods as you want.
