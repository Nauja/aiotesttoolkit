# Run parent directory as: python test/__init__.py
import aiotesttoolkit


def main():
    aiotesttoolkit.setup_logging()

    aiotesttoolkit.run(
        "test/ConfigLight.json", parent_module=None, cover_package="aiotesttoolkit",
    )


if __name__ == "__main__":
    main()
