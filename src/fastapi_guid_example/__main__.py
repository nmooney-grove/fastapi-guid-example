"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """FastAPI GUID Example."""


if __name__ == "__main__":
    main(prog_name="fastapi-guid-example")  # pragma: no cover
