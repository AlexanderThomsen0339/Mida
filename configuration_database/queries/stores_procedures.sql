USE Configuration_database;
GO

-- ============================================================
-- SP: Opret nyt job
-- Returnerer det nye JobID
-- ============================================================
CREATE OR ALTER PROCEDURE sp_CreateJob
    @SourceID   INT,
    @Status     NVARCHAR(50) = 'pending'
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO Jobs (SourceID, Timestamp, Status)
    VALUES (@SourceID, GETDATE(), @Status);

    SELECT SCOPE_IDENTITY() AS JobID;
END;
GO

-- ============================================================
-- SP: Opdater status på et job
-- ============================================================
CREATE OR ALTER PROCEDURE sp_UpdateJobStatus
    @JobID      INT,
    @Status     NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE Jobs
    SET Status = @Status
    WHERE JobID = @JobID;
END;
GO

-- ============================================================
-- SP: Indsæt log-entry
-- ============================================================
CREATE OR ALTER PROCEDURE sp_InsertJobLog
    @JobID      INT,
    @Type       NVARCHAR(50),
    @Message    NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO Job_logs (JobID, Timestamp, Type, Message)
    VALUES (@JobID, GETDATE(), @Type, @Message);
END;
GO