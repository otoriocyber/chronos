import os
from parsers_wrapper import parsers_wrapper


def get_all_funcs():
    """
    Get all the public functions from the wrapper module
    """
    funcs = []
    for i in dir(parsers_wrapper):
        item = getattr(parsers_wrapper, i)
        if callable(item) and not item.__name__.startswith("__"):
            funcs.append(item)

    return funcs


def create_temp_dir(date, hostname):
    # A temporary directory that will store the results of some of the parsers in the middle stage
    temp_path = "temp_results\\{hostname}-{date}".format(hostname=hostname, date=date)
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    return temp_path


