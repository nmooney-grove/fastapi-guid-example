"""Entrypoint."""
import uvicorn


def main() -> None:
    """FastAPI GUID Example."""
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()  # pragma: no cover
