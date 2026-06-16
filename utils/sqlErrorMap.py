SQLITE_ERROR_MAP = {
    "SQLITE_CONSTRAINT_UNIQUE": (409, "Resource already exists"),
    "SQLITE_CONSTRAINT_FOREIGNKEY": (400, "Invalid reference"),
    "SQLITE_CONSTRAINT_NOTNULL": (400, "Missing required field"),
    "SQLITE_CONSTRAINT_PRIMARYKEY": (409, "Duplicate primary key"),
    "SQLITE_CONSTRAINT_CHECK": (400, "Validation failed"),
}
