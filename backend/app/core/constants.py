class Severity:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    ORDER = [INFO, LOW, MEDIUM, HIGH, CRITICAL]

    WEIGHTS = {
        CRITICAL: 40,
        HIGH: 25,
        MEDIUM: 12,
        LOW: 5,
        INFO: 1,
    }


class Category:
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    QUALITY = "quality"


class RunStatus:
    QUEUED = "queued"
    FETCHING = "fetching"
    ANALYZING = "analyzing"
    REASONING = "reasoning"
    VERIFYING = "verifying"
    POSTING = "posting"
    COMPLETED = "completed"
    FAILED = "failed"


class VerdictAction:
    APPROVE = "APPROVE"
    COMMENT = "COMMENT"
    REQUEST_CHANGES = "REQUEST_CHANGES"
