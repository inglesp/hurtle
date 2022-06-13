import csv


class CSVTable:
    def __init__(self, filename):
        self.filename = filename

    @property
    def schema(self):
        with open(self.filename) as f:
            reader = csv.reader(f)
            return next(reader)

    def select(self):
        with open(self.filename) as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                yield row
