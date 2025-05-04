from abc import abstractmethod, ABC
from enum import IntEnum
from typing import Generic, Any, Iterator, Self, Callable, overload

import pandas as pd

from src.models.data.light_dc import GenericLightDc
from src.tools.serialization import simplify_type


class LdcFrame(Generic[GenericLightDc], ABC):
    # A dataframe representing an indexed list of light dataclass objects

    @classmethod
    @abstractmethod
    def _get_dc_type(cls) -> type[GenericLightDc]:
        ...

    def __init__(self, dcs: list[GenericLightDc] | pd.DataFrame) -> None:
        if isinstance(dcs, list):
            assert len(dcs) > 0
            assert [isinstance(dc, self._get_dc_type()) for dc in dcs]

            df = pd.concat(
                objs=[pd.Series(dc.to_simple_dict()) for dc in dcs],
                axis=1,
                ignore_index=True,
            ).T
            dtypes = {k: type(v) for k, v in dcs[0].to_simple_dict().items()}
            df = df.astype(dtypes)

            df.set_index("id", inplace=True, drop=True)
        else:
            assert isinstance(dcs, pd.DataFrame)
            df = dcs.copy(deep=True)

        assert df.index.is_unique, f"Ids are not unique: {df.index.duplicated()}"
        self._df = df

    @overload
    def __getitem__(self, index: int) -> GenericLightDc:
        ...

    @overload
    def __getitem__(self, index: str) -> pd.Series:
        ...

    def __getitem__(self, x: int | str) -> GenericLightDc | pd.Series:
        if isinstance(x, str):
            return self._df.loc[:, x].copy(deep=True)
        assert isinstance(x, int)

        if x not in self._df.index:
            raise KeyError(f"Element with id {x} not found in {self.__class__.__name__}")
        row = self._df.loc[x]
        return self._get_dc_type().from_simple_dict({**row.to_dict(), "id": x})

    def __iter__(self) -> Iterator[GenericLightDc]:
        for dc_id in self._df.index:
            yield self[dc_id]

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} ({len(self._df)} rows)>"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:\n{repr(self._df)}"

    def __add__(self, other: Self | GenericLightDc) -> Self:
        if isinstance(other, self.__class__):
            return self.__class__(pd.concat([self._df, other._df], axis=0))
        elif isinstance(other, self._get_dc_type()):
            return self.__class__(pd.concat([self._df, pd.DataFrame([other.to_simple_dict()])], axis=0))
        else:
            raise TypeError(f"Cannot add {type(other)} to {type(self)}")

    @property
    def df(self) -> pd.DataFrame:
        return self._df.copy(deep=True)

    def filter(self, condition: dict[str, Any] | Callable[[pd.Series], bool]) -> Self:
        """
        Filters the LdcFrame based on the given condition and returns a new version.
        :param condition: Either
        Fast and easy: A dictionary of key-value pairs to filter on
        OR
        Advanced: A function that is called on the underlying series

        >>> class Color(IntEnum):
        >>>    Red = 1
        >>>
        >>> self.filter({"bus1": 1, "color": Color.Red))
        >>> self.filter(lambda x: x["bus1"] == 1 and x["color"] == simplify_type(Color.Red))

        # Note that in the advanced case, the function is called on the underlying series which cannot contain complex types
        # Make sure to convert to simple types before using them in the function
        :return: The filtered LdcFrame
        """
        # Check if it is callable
        if callable(condition):
            filtered_df = self._df[self._df.apply(condition, axis=1)]
        else:
            assert isinstance(condition, dict)
            condition = {k: simplify_type(x=v) for k, v in condition.items()}
            filtered_df = self._df[
                self._df[list(condition.keys())].eq(pd.Series(condition)).all(axis=1)
            ]
        return self.__class__(filtered_df)


    def drop_items(self, condition: list[int] | dict[str, Any] | Callable[[pd.Series], bool]) -> Self:
        """
        :param condition: Either a list of keys to drop or a condition to filter on (see filter method)
        :return: A new version of the LdcFrame with the items dropped
        """
        if isinstance(condition, list):
            keys = condition
        else:
            keys = self.filter(condition=condition).df.index
        return self.__class__(self._df.drop(keys, axis=0))

    def as_objs(self) -> list[GenericLightDc]:
        return list(self.__iter__())

    def to_simple_dict(self) -> dict[str, Any]:
        # Returns a dict representation of the frame
        return {
            "class": self.__class__.__name__,
            "data": [dc.to_simple_dict() for dc in self],
        }

    @classmethod
    def from_simple_dict(cls, data: dict) -> Self:
        # Creates a frame from a dict representation
        assert data["class"] == cls.__name__, f"Class mismatch: {data['class']} != {cls.__name__}"
        dcs = [cls._get_dc_type().from_simple_dict(dc) for dc in data["data"]]
        return cls(dcs)
