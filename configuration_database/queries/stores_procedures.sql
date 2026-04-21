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

-- ============================================================
-- SP: Hent kilder
-- ============================================================
CREATE OR ALTER PROCEDURE sp_GetSources
    @SourceID INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        SourceID,
        SourceName,
        Source_URL,
        Authentication,
        UPDATED_AT
    FROM dbo.Sources
    WHERE @SourceID IS NULL OR SourceID = @SourceID;
END;
GO

-- ============================================================
-- SP: Hent jobs
-- ============================================================

CREATE PROCEDURE sp_GetJobs
AS
BEGIN
    SET NOCOUNT ON;
    SELECT JobID, SourceID, Timestamp, Status
    FROM dbo.Jobs
    ORDER BY Timestamp DESC;
END;
GO

-- ============================================================
-- SP: Hent Logs for et job
-- ============================================================

CREATE PROCEDURE sp_GetJobLogs
    @JobID INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT RunID, JobID, Timestamp, Type, Message
    FROM dbo.Job_logs
    WHERE JobID = @JobID
    ORDER BY Timestamp ASC;
END;
GO

-- ============================================================
-- SP: Hent bruger
-- ============================================================

CREATE PROCEDURE sp_GetUser
    @Username NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT UserID, Username, Password
    FROM dbo.Users
    WHERE Username = @Username;
END;
GO