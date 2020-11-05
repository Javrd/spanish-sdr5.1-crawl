def find_index(flist, func):
    for i, v in enumerate(flist):
        if func(v): return i
    return -1
