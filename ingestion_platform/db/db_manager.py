"""
db_manager.py
-------------
Håndterer forbindelse til Configuration_database og kalder stored procedures
for job-styring og logging.
Kræver: pip install pyodbc python-dotenv
"""
import os
import logging
import pyodbc
from contextlib import contextmanager
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env", override=True)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Forbindelses-hjælper
# ---------------------------------------------------------------------------
def _build_connection_string() -> str:
    return (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.environ['DB_SERVER']};"
        f"DATABASE={os.environ.get('DB_NAME', 'Configuration_database')};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )


@contextmanager
def get_connection():
    """
    Context manager der åbner og lukker en databaseforbindelse automatisk.

    Eksempel:
        with get_connection() as conn:
            ...
    """
    conn = pyodbc.connect(_build_connection_string(), timeout=10)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Stored procedures
# ---------------------------------------------------------------------------

def create_job(source_id: int, status: str = "pending") -> int:
    """
    Kalder sp_CreateJob og returnerer det nye JobID.

    Args:
        source_id: ID på kilden jobbet tilhører.
        status:    Startstatus, default 'pending'.

    Returns:
        JobID (int) for det oprettede job.
    """
    sql = "EXEC sp_CreateJob @SourceID = ?, @Status = ?;"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, source_id, status)

        # pyodbc springer nogle gange tomme result sets over (fx rowcount-sets
        # fra INSERT) — vi løber igennem dem alle til vi finder en rækk med data.
        row = None
        while row is None:
            row = cursor.fetchone()
            if row is not None:
                break
            if not cursor.nextset():
                break

        if row is None:
            raise RuntimeError(
                "sp_CreateJob returnerede ingen rækker — "
                "tjek at SELECT SCOPE_IDENTITY() er til stede i SP'en."
            )

        job_id = int(row[0])  # kolonneindeks i stedet for navn, mere robust

    log.info("Job oprettet — JobID=%d, SourceID=%d, Status='%s'", job_id, source_id, status)
    return job_id


def update_job_status(job_id: int, status: str) -> None:
    """
    Kalder sp_UpdateJobStatus og opdaterer status på et eksisterende job.

    Args:
        job_id: ID på jobbet der skal opdateres.
        status: Ny status, f.eks. 'running', 'success', 'failed'.
    """
    sql = "EXEC sp_UpdateJobStatus @JobID = ?, @Status = ?;"
    with get_connection() as conn:
        conn.cursor().execute(sql, job_id, status)
    log.info("Job opdateret — JobID=%d → Status='%s'", job_id, status)


def insert_job_log(job_id: int, log_type: str, message: str) -> None:
    """
    Kalder sp_InsertJobLog og indsætter en log-linje til et job.

    Args:
        job_id:   ID på det job loggen tilhører.
        log_type: Kategori, f.eks. 'INFO', 'WARNING', 'ERROR'.
        message:  Beskedens indhold.
    """
    sql = "EXEC sp_InsertJobLog @JobID = ?, @Type = ?, @Message = ?;"
    with get_connection() as conn:
        conn.cursor().execute(sql, job_id, log_type, message)
    log.debug("Log indsat — JobID=%d, Type='%s'", job_id, log_type)

def get_sources() -> list[dict]:
    """
    Kalder sp_GetSources og returnerer alle kilder som en liste af dicts.
    """
    sql = "EXEC sp_GetSources @SourceID = NULL;"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
def get_source(source_id: int) -> dict | None:
    """
    Kalder sp_GetSources med et specifikt SourceID og returnerer kilden som dict.
    Returnerer None hvis kilden ikke findes.
    """
    sql = "EXEC sp_GetSources @SourceID = ?;"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, source_id)
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


# ---------------------------------------------------------------------------
# Convenience wrapper – bruges af writeren
# ---------------------------------------------------------------------------

class Configuration_manager:
    """
    Høj-niveau wrapper der styrer et enkelt job fra start til slut.

    Eksempel:
        cm = Configuration_manager(source_id=3)
        cm.start()
        try:
            # ... skriv data til lake ...
            cm.success("Fil gemt: kilde/2025/04/14/10/30/data.parquet")
        except Exception as e:
            cm.fail(str(e))
    """

    def __init__(self, source_id: int):
        self.source_id = source_id
        self.job_id: int | None = None

    # --- livscyklus ---

    def start(self) -> int:
        """Opretter job i databasen og sætter status til 'running'."""
        self.job_id = create_job(self.source_id, status="pending")
        update_job_status(self.job_id, "running")
        insert_job_log(self.job_id, "INFO", "Job startet.")
        return self.job_id

    def success(self, message: str = "Job afsluttet uden fejl.") -> None:
        """Markerer jobbet som 'success' og indsætter en INFO-log."""
        job_id = self._require_started()
        insert_job_log(job_id, "INFO", message)
        update_job_status(job_id, "success")

    def fail(self, error_message: str) -> None:
        """Markerer jobbet som 'failed' og indsætter en ERROR-log."""
        job_id = self._require_started()
        insert_job_log(job_id, "ERROR", error_message)
        update_job_status(job_id, "failed")

    def log(self, message: str, log_type: str = "INFO") -> None:
        """Indsætter en vilkårlig log-linje under det kørende job."""
        job_id = self._require_started()
        insert_job_log(job_id, log_type, message)

    # --- intern hjælper ---

    def _require_started(self) -> int:
        """Returnerer job_id som int, eller kaster RuntimeError hvis .start() ikke er kaldt."""
        if self.job_id is None:
            raise RuntimeError("Kald .start() før du bruger JobManager.")
        return self.job_id


# ---------------------------------------------------------------------------
# Hurtig manuel test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cm = Configuration_manager(source_id=1)
    cm.start()
    cm.log("Henter data fra kilde...")
    cm.success("Testjob gennemført.")
    print(f"Job {cm.job_id} afsluttet korrekt.")