"""
ingestion_runner.py
-------------------
Generisk ingestion-runner der modtager en liste af kilder fra orkestratoren
og kører det kildespecifikke script for hver kilde parallelt.

Mappestruktur der forventes:
    sources/
        source_1/
            ingest.py        ← skal indeholde en run(config: dict) -> pd.DataFrame
        source_2/
            ingest.py
        ...

Lake-struktur der skrives til:
    <lake_root>/<source_name>/<år>/<måned>/<dag>/<time>/<minut>/data.parquet

Kræver: pip install pyodbc python-dotenv pandas pyarrow
"""

import importlib.util
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import pandas as pd

from db.db_manager import Configuration_manager

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Konstanter
# ---------------------------------------------------------------------------
SOURCES_DIR = Path(os.environ.get("SOURCES_DIR", "sources"))
LAKE_ROOT   = Path(os.environ.get("LAKE_ROOT",   "lake"))


# ---------------------------------------------------------------------------
# Lake-sti hjælper
# ---------------------------------------------------------------------------
def _lake_path(source_name: str, ts: datetime) -> Path:
    """
    Returnerer den fulde sti til parquet-filen for en given kilde og tidspunkt.

    Eksempel: lake/vejr/2025/04/14/10/30/data.parquet
    """
    return (
        LAKE_ROOT
        / source_name
        / ts.strftime("%Y")
        / ts.strftime("%m")
        / ts.strftime("%d")
        / ts.strftime("%H")
        / ts.strftime("%M")
        / "data.parquet"
    )


# ---------------------------------------------------------------------------
# Dynamisk loader af kildespecifikt script
# ---------------------------------------------------------------------------
def _load_source_module(source_name: str):
    """
    Loader sources/<source_name>/ingest.py dynamisk og returnerer modulet.
    Modulet skal eksponere: run(config: dict) -> pd.DataFrame
    """
    script_path = SOURCES_DIR / source_name / "ingest.py"
    if not script_path.exists():
        raise FileNotFoundError(
            f"Ingest-script ikke fundet: {script_path}"
        )

    spec = importlib.util.spec_from_file_location(
        f"sources.{source_name}.ingest", script_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Kunne ikke loade spec for '{source_name}' — tjek at filen er gyldig Python."
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    if not hasattr(module, "run"):
        raise AttributeError(
            f"{script_path} mangler en run(config)-funktion."
        )

    return module


# ---------------------------------------------------------------------------
# Kør én kilde
# ---------------------------------------------------------------------------
def run_source(source: dict) -> bool:
    """
    Kører ingestion for én kilde.

    Args:
        source: Dict med mindst:
            - "source_id"   (int)  — ID i Configuration_database
            - "source_name" (str)  — mappenavn under sources/
            - "config"      (dict) — vilkårlig konfiguration til ingest.py

    Returns:
        True hvis succes, False hvis fejl.
    """
    source_id   = source["source_id"]
    source_name = source["source_name"]
    config      = source.get("config", {})

    cm = Configuration_manager(source_id=source_id)
    cm.start()

    try:
        # --- 1. Load kildespecifikt script ---
        cm.log(f"Loader ingest-script for '{source_name}'.")
        module = _load_source_module(source_name)

        # --- 2. Hent data fra API ---
        cm.log("Henter data fra API...")
        df: pd.DataFrame = module.run(config)

        if df is None or df.empty:
            cm.log("API returnerede ingen data — springer over.", "WARNING")
            cm.success("Afsluttet uden data.")
            return True

        cm.log(f"Modtaget {len(df):,} rækker fra API.")

        # --- 3. Byg lake-sti og gem som parquet ---
        ts        = datetime.now()
        out_path  = _lake_path(source_name, ts)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_parquet(out_path, index=False, engine="pyarrow")
        cm.log(f"Data gemt: {out_path}")

        # --- 4. Afslut job ---
        cm.success(f"Ingestion fuldført — {len(df):,} rækker → {out_path}")
        return True

    except Exception as exc:
        log.exception("Fejl under ingestion af '%s'", source_name)
        cm.fail(str(exc))
        return False


# ---------------------------------------------------------------------------
# Hoved-runner — kaldes af orkestratoren
# ---------------------------------------------------------------------------
def run_ingestion(sources: list[dict], max_workers: int = 4) -> dict:
    """
    Kører ingestion for en liste af kilder parallelt.

    Args:
        sources:     Liste af source-dicts (se run_source for format).
        max_workers: Antal samtidige tråde — sættes af orkestratoren.

    Returns:
        Dict med opsummering:
            {
                "total":   int,
                "success": int,
                "failed":  int,
                "results": { source_name: bool, ... }
            }
    """
    results  = {}
    success  = 0
    failed   = 0

    log.info(
        "Starter ingestion — %d kilde(r), %d worker(e).",
        len(sources), max_workers
    )

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(run_source, src): src["source_name"]
            for src in sources
        }

        for future in as_completed(futures):
            name = futures[future]
            try:
                ok = future.result()
            except Exception as exc:
                log.error("Uventet fejl for '%s': %s", name, exc)
                ok = False

            results[name] = ok
            if ok:
                success += 1
            else:
                failed += 1

    summary = {
        "total":   len(sources),
        "success": success,
        "failed":  failed,
        "results": results,
    }

    log.info(
        "Ingestion færdig — %d/%d succesfulde.",
        success, len(sources)
    )
    return summary


# ---------------------------------------------------------------------------
# Eksempel på direkte kørsel (uden orkestrator)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_sources = [
        {
            "source_id":   1,
            "source_name": "vejr",
            "config": {
                "api_url": "https://api.example.com/vejr",
                "api_key": "hemlig-nøgle",
            },
        },
    ]

    summary = run_ingestion(test_sources, max_workers=2)
    print(summary)