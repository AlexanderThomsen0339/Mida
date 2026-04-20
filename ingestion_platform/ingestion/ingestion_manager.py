"""
ingestion_manager.py
--------------------
Kører ingestion for en liste af kilder parallelt.
Kaldes af orkestratoren.
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from ingestion_platform.db.db_manager import Configuration_manager, log
import importlib

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

    log.info("Ingestion færdig — %d/%d succesfulde.", success, len(sources))
    return {"total": len(sources), "success": success, "failed": failed, "results": results}