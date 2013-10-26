
def diffDicts(d1, d2, hashfunc, both_ref=None):
    """
        diff two list of dicts by hashing each dict
        returns (only_in_d1, only_in_d2, in_both)
        in_both references object in d1
    """
    o_map = {}
    for o in d1:
        o_map[hashfunc(o)] = o
    both = []
    only_d2 = []
    for o in d2:
        hashd = hashfunc(o)
        if hashd in o_map:
            if both_ref is d2:
                both.append(o)
                o_map.pop(hashd)
            else:
                both.append(o_map.pop(hashd))
        else:
            only_d2.append(o)
    only_d1 = o_map.values()
    return (only_d1, only_d2, both)


def progHash(d):
    hashkeys = ['id', 'name', 'url', 'channel']
    return dictHashHelper(d, hashkeys)


def episodeHash(d):
    hashkeys = ['name', 'url']
    return dictHashHelper(d, hashkeys)


def dictHashHelper(d, hashkeys):
    hashed_values = map(hash, [v for k, v in d.items() if k in hashkeys])
    return sum(hashed_values)
