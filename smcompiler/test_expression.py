"""
Unit tests for expressions.
Testing expressions is not obligatory.

MODIFY THIS FILE.
"""

from expression import Secret, Scalar


# Example test, you can adapt it to your needs.
def test_expr_construction():
    a = Secret(1)
    b = Secret(2)
    c = Secret(3)
    expr = (a + b) * c * Scalar(4) + Scalar(3)
    assert repr(expr) == "((Secret(1) + Secret(2)) * Secret(3) * Scalar(4) + Scalar(3))"

def test_add_None1():
    a = Secret()
    b = Secret(2)
    expr = a + b
    assert repr(expr) == "(Secret() + Secret(2))"


def test_add_None2():
    a = Secret(2)
    b = Secret()
    expr = a + b
    assert repr(expr) == "(Secret(2) + Secret())"

def test_add_None3():
    a = Secret()
    b = Secret()
    expr = a + b
    assert repr(expr) == "(Secret() + Secret())"

def test_sub_None1():
    a = Secret()
    b = Secret(2)
    expr = a - b
    assert repr(expr) == "(Secret() - Secret(2))"


def test_sub_None2():
    a = Secret(2)
    b = Secret()
    expr = a - b
    assert repr(expr) == "(Secret(2) - Secret())"

def test_sub_None3():
    a = Secret()
    b = Secret()
    expr = a - b
    assert repr(expr) == "(Secret() - Secret())"


def test_mul_None1():
    a = Secret()
    b = Secret(2)
    expr = a * b
    assert repr(expr) == "Secret() * Secret(2)"


def test_mul_None2():
    a = Secret(2)
    b = Secret()
    expr = a * b
    assert repr(expr) == "Secret(2) * Secret()"

def test_mul_None3():
    a = Secret()
    b = Secret()
    expr = a * b
    assert repr(expr) == "Secret() * Secret()"