import os.path
import glob


def get_local_plugins():
    """Get plugins names from local path."""

    # Set plugins path
    path = "../../plugins/*"

    # Get plugins file names
    files = glob.glob(path)

    # Filter file names by basename and capitalize
    names = [os.path.basename(x).capitalize() for x in files]

    return names
