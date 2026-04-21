USE Configuration_database;
GO

CREATE TABLE Sources (
    SourceID       INT            PRIMARY KEY IDENTITY(1,1),
    SourceName     NVARCHAR(255)  NOT NULL,
    Source_URL     NVARCHAR(MAX)  NOT NULL,
    Authentication NVARCHAR(MAX)  NULL,
    UPDATED_AT     DATETIME       DEFAULT GETDATE()
);
GO

CREATE TABLE Jobs (
    JobID      INT          PRIMARY KEY IDENTITY(1,1),
    SourceID   INT          NOT NULL,
    Timestamp  DATETIME     DEFAULT GETDATE(),
    Status     NVARCHAR(50),
    CONSTRAINT FK_Jobs_Sources FOREIGN KEY (SourceID)
        REFERENCES Sources(SourceID)
);
GO

CREATE TABLE Job_logs (
    RunID     INT           PRIMARY KEY IDENTITY(1,1),
    JobID     INT           NOT NULL,
    Timestamp DATETIME      DEFAULT GETDATE(),
    Type      NVARCHAR(50)  NOT NULL,
    Message   NVARCHAR(MAX) NOT NULL,
    CONSTRAINT FK_Joblogs_Jobs FOREIGN KEY (JobID)
        REFERENCES Jobs(JobID)
);
GO

CREATE OR ALTER PROCEDURE sp_GetSources
    @SourceID INT = NULL   -- NULL = hent alle, ellers hent specifik kilde
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        SourceID,
        SourceName,
        Source_URL,
        Authentication
    FROM Sources
    WHERE @SourceID IS NULL
       OR SourceID = @SourceID;
END;
GO

CREATE TABLE Users (
    UserID    INT IDENTITY PRIMARY KEY,
    Username  NVARCHAR(100) NOT NULL UNIQUE,
    Password  NVARCHAR(255) NOT NULL,  -- bcrypt hash
    CreatedAt DATETIME DEFAULT GETDATE()
);