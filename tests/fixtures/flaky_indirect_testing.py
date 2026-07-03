"""
Fixture: Indirect Testing smell - FLAKY pattern

Tests that verify behavior through deeply nested objects
rather than testing the subject directly.
"""


class Database:
    def __init__(self):
        self.connection = Connection()


class Connection:
    def __init__(self):
        self.cursor = Cursor()


class Cursor:
    def __init__(self):
        self.result = Result()


class Result:
    def __init__(self):
        self.data = [1, 2, 3]


def test_database_through_chain():
    """Bad: Tests database through deeply nested access."""
    db = Database()

    # Testing through multiple levels of indirection
    assert db.connection.cursor.result.data == [1, 2, 3]


def test_indirect_attribute_access():
    """Bad: Asserts on deeply nested properties."""
    db = Database()

    # Multiple levels of attribute traversal
    assert len(db.connection.cursor.result.data) == 3
