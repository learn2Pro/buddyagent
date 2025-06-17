import pytest
import sys
import os
from typing import Annotated, List, Optional

def add(x, y):
    return x + y

def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y

def test_add():
    print(1)
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_divide():
    print(2)
    assert divide(10, 2) == 5

def test_divide_by_zero():
    with pytest.raises(ValueError, match="divide by zero"):
        divide(10, 0)