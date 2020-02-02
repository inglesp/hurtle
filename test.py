from chortle import build_extension, Function


if __name__ == "__main__":
    functions = [
        Function("rot13", "test_fns.rot13"),
        Function("product", "test_fns.product"),
    ]
    build_extension("testplg", functions=functions, verbose=True)
