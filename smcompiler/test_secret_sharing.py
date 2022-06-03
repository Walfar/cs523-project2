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
    assert(share1 + share2 == Share(38+77%p))
    assert(share1 - share2 == Share(38-77%p))
    assert(share1 * share2 == Share(38*77%p))

def test_2() :
    share1 = Share(p-1)
    share2 = Share(1)
    share3 = Share(2)
    assert(share1 + share2 == Share(0))
    assert(share1 - share2 == Share(p-2))
    assert(share1 * share3 == Share(p-2))

def test_share_secret1() :
    secret = 100
    shares = share_secret(secret,10)
    assert(reconstruct_secret(shares) == secret)

def test_share_secret2() :
    secret = p-10
    shares = share_secret(secret,p-100)
    assert(reconstruct_secret(shares) == secret)

def test_share_secret3() :
    secret = 2345
    shares = share_secret(secret,100)
    assert(reconstruct_secret(shares) == secret)