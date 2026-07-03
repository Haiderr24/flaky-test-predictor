"""
Fixture: Eager Testing smell - FLAKY pattern

Tests that exercise too many methods at once are fragile and
hard to maintain - any change to any method breaks the test.
"""


class UserService:
    def create(self, name):
        return {"name": name, "id": 1}

    def validate(self, user):
        return True

    def save(self, user):
        return True

    def notify(self, user):
        return True

    def log(self, user):
        return True

    def cache(self, user):
        return True

    def index(self, user):
        return True


def test_user_workflow_eager():
    """Bad: Tests too many things at once."""
    service = UserService()

    user = service.create("Alice")
    assert service.validate(user)
    assert service.save(user)
    assert service.notify(user)
    assert service.log(user)
    assert service.cache(user)
    assert service.index(user)
    # If any method changes, this whole test breaks
