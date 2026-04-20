"""
Kalder en enkelt extractor i ingestion/sources/ og gemmer data i Laken.
Bruges til manuel kørsel og test af en enkelt kilde, fx under udvikling.
"""
import importlib
from db.db_manager import get_source, Configuration_manager, log


def get_ingestor_class(source_name: str):
    """Loader dynamisk ingestor-klassen baseret på source_name fra databasen."""
    try:
        module = importlib.import_module(f"ingestion.sources.{source_name}")
        class_name = f"{source_name.capitalize()}Ingestor"
        return getattr(module, class_name)
    except (ModuleNotFoundError, AttributeError) as e:
        log.warning("Ingen ingestor fundet for '%s': %s", source_name, e)
        return None


def run(source_id: int) -> None:
    source = get_source(source_id)
    if not source:
        log.error("Ingen kilde fundet med SourceID=%d.", source_id)
        return

    source_name = source["SourceName"]

    ingestor_class = get_ingestor_class(source_name)
    if ingestor_class is None:
        return

    cf = Configuration_manager(source_id=source_id)
    cf.start()

    try:
        ingestor = ingestor_class(source_id, source_name, {
            "api_url":        source["Source_URL"],
            "authentication": source["Authentication"],
        })
        ingestor.run()
        cf.success(f"{source_name} ingestering gennemført.")
    except Exception as e:
        cf.fail(str(e))