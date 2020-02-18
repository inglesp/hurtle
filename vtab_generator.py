def generate_series(start, stop, step=1, order_by=None):
    series = range(start, stop, step)

    if (order_by == ["-value"] and step > 0) or (order_by != ["-value"] and step < 0):
        series = reversed(series)

    for value in series:
        yield value
