class DummyConnection:
    def commit(self):
        return None

    def rollback(self):
        return None


def connect(_url=None):
    return DummyConnection()
