from chortle import ExtensionBuilder


if __name__ == '__main__':
    builder = ExtensionBuilder('testplg', verbose=True)
    builder.add_function('rot13', 'test_fns.rot13')
    builder.add_function('product', 'test_fns.product')
    builder.build()
