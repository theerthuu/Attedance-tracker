import os
import getpass

def get_data_path():
    """
    Returns a user-specific attendance.csv path.
    Auto-creates directory if not present.
    """
    username = getpass.getuser()
    base_dir = os.path.expanduser("~")
    data_dir = os.path.join(base_dir, "attendance_tracker")

    os.makedirs(data_dir, exist_ok=True)

    return os.path.join(data_dir, "attendance.csv")
