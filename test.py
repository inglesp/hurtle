from chortle import build_extension


if __name__ == "__main__":
    build_extension(
        "testplg",
        functions={
            "rot13": "test_fns.rot13",
            "product": "test_fns.product",
        },
        verbose=True,
    )
