# Run parent directory as: python test/__init__.py
import aiotesttoolkit
from aiotesttoolkit import loader


def main():
    aiotesttoolkit.setup_logging()

    loader.run(
        "test/Config.json",
        parent_module=None,
        cover_package="aiotesttoolkit",
    )


if __name__ == "__main__":
    main()
