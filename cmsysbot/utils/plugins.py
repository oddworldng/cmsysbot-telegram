import os.path
import glob


def get_local_plugins():

    path = "../../plugins/*"
    files = glob.glob(path)

    names = [os.path.basename(x) for x in files]
    return names