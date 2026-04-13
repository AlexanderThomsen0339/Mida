import os
import json
from datetime import datetime


LAKE_BASE_PATH = os.getenv("LAKE_BASE_PATH", "./lake/bronze")


def write_to_bronze(source_name: str, data: dict | list) -> str:
    """
    Skriver råt JSON til bronze-laget i data lake'en.

    Filstruktur:
    /lake/bronze/{source}/year={Y}/month={M}/day={D}/hour={H}/minute={Min}/raw.json

    Returnerer den fulde sti til den skrevne fil.
    """
    now = datetime.utcnow()

    path = os.path.join(
        LAKE_BASE_PATH,
        source_name,
        f"year={now.year}",
        f"month={now.month:02d}",
        f"day={now.day:02d}",
        f"hour={now.hour:02d}",
        f"minute={now.minute:02d}",
    )

    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, "raw.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return file_path


if __name__ == "__main__":
    test_data = {"test": True, "message": "Hello from bronze layer"}
    result = write_to_bronze("test_source", test_data)
    print(f"Skrevet til: {result}")