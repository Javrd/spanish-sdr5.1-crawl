def find_index(flist, func):
    for idx, var in enumerate(flist):
        if func(var):
            return idx
    return -1
