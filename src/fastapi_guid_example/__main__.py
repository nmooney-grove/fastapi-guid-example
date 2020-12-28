"""Entrypoint."""
import uvicorn


def main() -> None:
    """Startup the Server."""
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()  # pragma: no cover
