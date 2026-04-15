"""
orchestrator.py
---------------
Orkestrator der henter kilder fra Configuration_database og
trigger ingestion_manager for det antal kilder orkestratoren
er konfigureret til at køre parallelt.

Kan køres:
    Tidsplan (cron/task scheduler):
        python orchestrator.py

    Manuelt med specifikt SourceID:
        python orchestrator.py --source-id 3
"""

import argparse
import logging
import sys

import pyodbc

from db.db_manager import get_connection
from ingestion.ingestion_manager import run_ingestion

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Konfiguration — justér disse værdier
# ---------------------------------------------------------------------------
MAX_WORKERS = 4   # antal kilder der køres parallelt


# ---------------------------------------------------------------------------
# Hent kilder fra databasen via SP
# ---------------------------------------------------------------------------
def fetch_sources(source_id: int | None = None) -> list[dict]:
    """
    Kalder sp_GetSources og returnerer en liste af kilder.

    Args:
        source_id: Specifikt SourceID ved manuel kørsel, None = alle kilder.

    Returns:
        Liste af dicts med SourceID, SourceName, Source_URL, Authentication.
    """
    sql = "EXEC sp_GetSources @SourceID = ?;"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, source_id)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

    sources = [dict(zip(columns, row)) for row in rows]

    if not sources:
        if source_id:
            log.warning("Ingen kilde fundet med SourceID=%d.", source_id)
        else:
            log.warning("Ingen kilder fundet i databasen.")

    return sources


# ---------------------------------------------------------------------------
# Byg source-dicts til ingestion_manager
# ---------------------------------------------------------------------------
def _build_ingestion_sources(db_sources: list[dict]) -> list[dict]:
    """
    Konverterer databaserækker til det format ingestion_manager forventer.

    ingestion_manager forventer:
        {
            "source_id":   int,
            "source_name": str,   ← bruges til at finde sources/<name>/ingest.py
            "config":      dict,  ← sendes til ingest.run(config)
        }
    """
    result = []
    for src in db_sources:
        result.append({
            "source_id":   src["SourceID"],
            "source_name": src["SourceName"],
            "config": {
                "api_url":        src["Source_URL"],
                "authentication": src["Authentication"],
            },
        })
    return result


# ---------------------------------------------------------------------------
# Hoved-funktion
# ---------------------------------------------------------------------------
def main(source_id: int | None = None) -> None:
    log.info(
        "Orkestrator starter — %s",
        f"SourceID={source_id}" if source_id else "alle kilder",
    )

    # --- 1. Hent kilder fra databasen ---
    db_sources = fetch_sources(source_id)
    if not db_sources:
        log.info("Ingen kilder at køre — afslutter.")
        sys.exit(0)

    log.info("Fandt %d kilde(r) i databasen.", len(db_sources))

    # --- 2. Byg til ingestion-format ---
    sources = _build_ingestion_sources(db_sources)

    # --- 3. Kør ingestion ---
    summary = run_ingestion(sources, max_workers=MAX_WORKERS)

    # --- 4. Opsummering ---
    log.info(
        "Orkestrator færdig — %d/%d succesfulde.",
        summary["success"], summary["total"],
    )

    if summary["failed"] > 0:
        log.warning("Fejlede kilder:")
        for name, ok in summary["results"].items():
            if not ok:
                log.warning("  ✗ %s", name)
        sys.exit(1)   # afslut med fejlkode så task scheduler/cron kan reagere

    sys.exit(0)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Kør ingestion for én eller alle kilder."
    )
    parser.add_argument(
        "--source-id",
        type=int,
        default=None,
        help="Kør kun én specifik kilde (manuelt). Udelad for at køre alle.",
    )
    args = parser.parse_args()
    main(source_id=args.source_id)