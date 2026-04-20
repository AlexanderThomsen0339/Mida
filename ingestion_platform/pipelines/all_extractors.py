"""
Kalder alle extractors i ingestion/sources/ og gemmer data i Laken.
"""
import importlib
from db.db_manager import get_sources, Configuration_manager, log


def get_ingestor_class(source_name: str):
    """Loader dynamisk ingestor-klassen baseret på source_name fra databasen."""
    try:
        module = importlib.import_module(f"ingestion.sources.{source_name}")
        class_name = f"{source_name.capitalize()}Ingestor"
        return getattr(module, class_name)
    except (ModuleNotFoundError, AttributeError) as e:
        log.warning("Ingen ingestor fundet for '%s': %s", source_name, e)
        return None


def run() -> None:
    for source in get_sources():
        source_name = source["SourceName"]
        source_id   = source["SourceID"]

        ingestor_class = get_ingestor_class(source_name)
        if ingestor_class is None:
            continue

        cf = Configuration_manager(source_id=source_id)
        cf.start()

        try:
            cf.success(f"{source_name} ingestering gennemført.")
        except Exception as e:
            cf.fail(str(e))


if __name__ == "__main__":
    run()