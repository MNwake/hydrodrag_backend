# main.py
import uvicorn
from core import HydrodragsApp

hydrodrags_app = HydrodragsApp()
app = hydrodrags_app.create_app()


def main() -> None:
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        # reload=True,
    )


if __name__ == "__main__":
    main()