"""
User roles enum for the application.

This enum defines the roles available in the system but is NOT stored in the database.
The database stores roles as dynamic strings, and this enum provides constants for
consistency in the codebase.
"""
import enum


class Roles(str, enum.Enum):
    """User roles enum - NOT stored in database, used for code consistency only"""
    ADMIN = "admin"
