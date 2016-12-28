class AutoVivification(dict):
    """
    Implementation of perl's autovivification feature and Cache's globals data structure.
    """

    def __getitem__(self, item):
        # print("get item")
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

    def __setitem__(self, key, value):
        # print("set item")
        if type(value) is type(self):
            return dict.__setitem__(self, key, value)
        else:
            return dict.__setitem__(self[key], None, value)
