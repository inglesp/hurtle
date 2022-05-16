class Table:
    tables = {}

    @classmethod
    def connect(cls, impl):
        key = len(cls.tables)
        table = cls(key, impl)
        cls.tables[key] = table
        return table

    def __init__(self, key, impl):
        self.key = key
        self.impl = impl
        self.cursors = {}

    def disconnect(self):
        del self.tables[self.key]


class Cursor:
    @classmethod
    def open(cls, table_key):
        table = Table.tables[table_key]
        cursor_key = len(table.cursors)
        table.cursors[cursor_key] = cls(cursor_key, table)
        return cursor_key

    def __init__(self, key, table):
        self.key = key
        self.table = table
        self.generator = None
        self.next_values = None
        self.done = False

    def step(self):
        assert self.generator is not None
        assert not self.done

        try:
            self.next_values = next(self.generator)
        except StopIteration:
            self.next_values = None
            self.done = True

    def close(self):
        del self.table.cursors[self.key]
