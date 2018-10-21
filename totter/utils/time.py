import datetime as dt


def now():
    return dt.datetime.now()


class WallTimer:
    def __init__(self):
        self.start = now()

    def __str__(self):
        return str(self.since())

    def start(self):
        self.start = now()

    def since(self):
        return now() - self.start
