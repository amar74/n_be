"""
Example unit test file
"""
import pytest
from faker import Faker

fake = Faker()


@pytest.mark.unit
def test_example_unit_test():
    """Example unit test"""
    assert 1 + 1 == 2


@pytest.mark.unit
def test_faker_example():
    """Example using Faker for test data"""
    email = fake.email()
    assert "@" in email
    assert len(email) > 0

