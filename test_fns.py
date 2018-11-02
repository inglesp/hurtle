import codecs
import functools


def rot13(inp):
    return codecs.encode(inp, 'rot_13')


def product(*args):
    return functools.reduce(lambda x, y: x * y, args, 1)
