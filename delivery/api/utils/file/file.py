class File:
    def __init__(self, bytes, name):
        self._bytes = bytes
        self._name = name

    @property
    def bytes(self):
        return self._bytes

    @property
    def name(self):
        return self._name

    @property
    def ext(self):
        return self._name.split('.')[-1]
