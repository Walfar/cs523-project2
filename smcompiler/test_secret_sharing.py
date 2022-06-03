"""
Unit tests for the secret sharing scheme.
Testing secret sharing is not obligatory.

MODIFY THIS FILE.
"""
import pytest
import secret_sharing
import sympy
from secret_sharing import p,Share,share_secret,reconstruct_secret
def test_p():
    assert(sympy.isprime(p))
    assert(p >= 2**29 and p <= 2**32)

def test_1() :
    share1 = Share(38)
    share2 = Share(77)
    share_add = share1 + share2
    share_sub = share2 - share1
    share_mul = share1 * share2
    assert(share_add.bn == 38+77%p)
    assert(share_sub.bn == 77-38%p)
    assert(share_mul.bn == 38*77%p)

def test_2() :
    share1 = Share(p-1)
    share2 = Share(1)
    share3 = Share(2)
    share_add = share1 + share2
    share_sub = share1 - share2
    share_mul = share1 * share3
    assert(share_add.bn == 0)
    assert(share_sub.bn == p-2)
    assert(share_mul.bn == p-2)

def test_share_secret1() :
    secret = 100
    shares = share_secret(secret,10)
    assert(reconstruct_secret(shares) == secret)

def test_share_secret2() :
    secret = 2345
    shares = share_secret(secret,100)
    assert(reconstruct_secret(shares) == secret)