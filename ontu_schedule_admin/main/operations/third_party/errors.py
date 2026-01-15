class ScheduleAPIError(ValueError):
    """Custom exception for Schedule API errors."""


class FacultyNotFoundError(ScheduleAPIError):
    """Exception raised when a faculty is not found."""


class GroupNotFoundError(ScheduleAPIError):
    """Exception raised when a group is not found."""


class IsOnBreakError(ScheduleAPIError):
    """Exception raised when the API is on break."""
