"""
ingestion_manager.py
--------------------
Kører ingestion for en liste af kilder parallelt.
Kaldes af orkestratoren.
"""
import json
import importlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from shared.db_manager import Configuration_manager, log

CACHE_PATH = Path(__file__).resolve().parent.parent / "serving" / "cache.json"


def _get_ingestor_class(source_name: str):
    module = importlib.import_module(f"ingestion_platform.ingestion.sources.{source_name}")
    class_name = f"{source_name.capitalize()}Ingestor"
    return getattr(module, class_name)


def run_source(source: dict) -> bool:
    source_id   = source["SourceID"]
    source_name = source["SourceName"]

    cm = Configuration_manager(source_id=source_id)
    cm.start()

    try:
        ingestor_class = _get_ingestor_class(source_name)
        ingestor = ingestor_class(source_id, source_name, {
            "api_url":        source["Source_URL"],
            "authentication": source["Authentication"],
        })
        ingestor.run()
        cm.success(f"{source_name} ingestering gennemført.")
        return True
    except Exception as e:
        log.exception("Fejl under ingestion af '%s': %s", source_name, e)
        cm.fail(str(e))
        return False


def _update_cache(succeeded_sources: list[str]) -> None:
    """Læser parquet for succeeded kilder og skriver til cache.json."""
    from ingestion_platform.serving.reader import get_latest_data

    cache = {}
    for source_name in succeeded_sources:
        try:
            cache[source_name] = get_latest_data(source_name, use_cache=False)
        except Exception as e:
            log.error("Kunne ikke cache '%s': %s", source_name, e)

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, default=str)

    log.info("Cache opdateret med %d kilde(r).", len(cache))


def run_ingestion(sources: list[dict], max_workers: int = 4) -> dict:
    results = {}
    success = 0
    failed  = 0

    log.info("Starter ingestion — %d kilde(r), %d worker(e).", len(sources), max_workers)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(run_source, src): src["SourceName"]
            for src in sources
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                ok = future.result()
            except Exception as e:
                log.error("Uventet fejl for '%s': %s", name, e)
                ok = False

            results[name] = ok
            success += ok
            failed  += not ok

    # Opdater cache med kun succeeded kilder
    succeeded = [name for name, ok in results.items() if ok]
    _update_cache(succeeded)

    log.info("Ingestion færdig — %d/%d succesfulde.", success, len(sources))
    return {"total": len(sources), "success": success, "failed": failed, "results": results}