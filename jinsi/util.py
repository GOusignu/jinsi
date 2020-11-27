class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def head(obj):
    return next(iter(obj))


def select(obj, *path, fallback=None):
    current = obj
    for element in path:
        try:
            current = current[element]
        except (KeyError, TypeError):
            return fallback
    return current
