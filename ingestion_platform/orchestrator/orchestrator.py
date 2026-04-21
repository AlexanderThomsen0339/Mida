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
import sys

from shared.db_manager import get_sources, get_source, log
from ingestion_platform.ingestion.ingestion_manager import run_ingestion

# ---------------------------------------------------------------------------
# Konfiguration — justér disse værdier
# ---------------------------------------------------------------------------
MAX_WORKERS = 4


# ---------------------------------------------------------------------------
# Hoved-funktion
# ---------------------------------------------------------------------------
def main(source_id: int | None = None) -> None:
    log.info(
        "Orkestrator starter — %s",
        f"SourceID={source_id}" if source_id else "alle kilder",
    )

    # --- 1. Hent kilder fra databasen ---
    sources = [get_source(source_id)] if source_id else get_sources()
    sources = [s for s in sources if s]  # filtrer None væk

    if not sources:
        log.warning("Ingen kilder fundet — afslutter.")
        sys.exit(0)

    log.info("Fandt %d kilde(r) i databasen.", len(sources))

    # --- 2. Kør ingestion ---
    summary = run_ingestion(sources, max_workers=MAX_WORKERS)

    # --- 3. Opsummering ---
    log.info(
        "Orkestrator færdig — %d/%d succesfulde.",
        summary["success"], summary["total"],
    )

    if summary["failed"] > 0:
        log.warning("Fejlede kilder:")
        for name, ok in summary["results"].items():
            if not ok:
                log.warning("  ✗ %s", name)
        sys.exit(1)

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