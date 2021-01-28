import datetime
import json
from typing import Iterator, Any, Union

from dezimal import Dezimal

INFINITY = float('inf')


class Encoder(json.JSONEncoder):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # noinspection PyMethodMayBeStatic
    def default_raw(self, o: Any) -> Union[str, type(None)]:
        return None

    def encode(self, o: Any) -> str:
        pieces = self.iterencode(o)
        return "".join(list(pieces))

    def iterencode(self, obj: Any, **kwargs) -> Iterator[str]:

        def floatstr(
                o,
                allow_nan=self.allow_nan,
                # check for specials. this type of test is platform-specific, so do tests which don't depend internals.
                _repr=repr,
                _inf=INFINITY,
                _neginf=-INFINITY
        ):

            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                return _repr(o)
            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))
            return text

        return _make_iterencode(
            encode_str=super().encode,
            encode_int=int.__repr__,
            encode_float=floatstr,
            encode_other_raw=self.default_raw,
            encode_other=self.default,
        )(obj)


# noinspection PyShadowingBuiltins
def _make_iterencode(
        encode_str,
        encode_int,
        encode_float,
        encode_other_raw,
        encode_other,
        # HACK: hand-optimized bytecode; turn globals into locals
        iter=iter,
        next=next,
        isinstance=isinstance,
        str=str,
        list=list,
        int=int,
        float=float,
        dec=Dezimal,
):
    def _iterencode_dict(o):
        it = iter(o.items())
        if not o:
            yield '{}'
            return
        yield '{'
        key, value = next(it)
        yield encode_str(str(key))
        yield ':'
        yield from _iterencode(value)
        for key, value in it:
            yield ','
            yield encode_str(str(key))
            yield ':'
            yield from _iterencode(value)
        yield '}'

    def _iterencode_list(o):
        if not o:
            yield '[]'
            return
        yield '['
        it = iter(o)
        item = next(it)
        yield from _iterencode(item)
        for item in it:
            yield ','
            yield from _iterencode(item)
        yield ']'

    def _iterencode(o):
        if isinstance(o, str):
            yield encode_str(o)
        elif o is None:
            yield 'null'
        elif o is True:
            yield 'true'
        elif o is False:
            yield 'false'
        elif isinstance(o, list):
            yield from _iterencode_list(o)
        elif isinstance(o, dec):
            yield str(o)
        elif isinstance(o, int):
            yield encode_int(o)
        elif isinstance(o, float):
            yield encode_float(o)
        elif isinstance(o, (datetime.date, datetime.datetime)):
            yield encode_str(str(o))
        else:
            try:
                yield from _iterencode_dict(o)
            except (TypeError, AttributeError):
                raw = encode_other_raw(o)
                if raw is not None:
                    yield raw
                else:
                    yield from _iterencode(encode_other(o))

    return _iterencode


def dumpjson(obj, **kwargs) -> str:
    return json.dumps(obj, cls=Encoder, **kwargs)


def loadjson(s):
    return json.loads(s)
