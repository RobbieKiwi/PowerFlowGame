from abc import abstractmethod, ABC
from typing import (
    Generic,
    Any,
    Iterator,
    Callable,
    overload,
    Literal,
    Optional,
    Iterable,
    TypeVar,
)

import pandas as pd
import numpy as np

from src.models.data.light_dc import T_LightDc
from src.tools.serialization import simplify_type
from src.tools.typing import T

Condition = dict[str, Any] | Callable[[pd.Series], bool]
Operator = Literal["or", "and", "not", None]


class LdcRepo(Generic[T_LightDc], ABC):
    # A dataframe-based repo containing an indexed list of light dataclass objects

    @classmethod
    @abstractmethod
    def _get_dc_type(cls) -> type[T_LightDc]: ...

    def __init__(self, dcs: list[T_LightDc] | pd.DataFrame) -> None:
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
            assert dcs.reset_index().columns.tolist() == self._get_dc_type().get_keys()
            df = dcs.copy(deep=True)

        assert df.index.is_unique, f"Ids are not unique: {df.index}"
        self._df = df

    @overload
    def __getitem__(self, index: int) -> T_LightDc: ...

    @overload
    def __getitem__(self, index: str) -> pd.Series: ...

    def __getitem__(self, x: int | str) -> T_LightDc | pd.Series:
        if isinstance(x, str):
            return self.df.loc[:, x]
        assert isinstance(x, int)
        simple_x = simplify_type(x)
        if simple_x not in self._df.index:
            raise KeyError(f"Element with id {x} not found in {self.__class__.__name__}")
        row = self.df.loc[simple_x]
        return self._get_dc_type().from_simple_dict({**row.to_dict(), "id": x})

    def __iter__(self) -> Iterator[T_LightDc]:
        for dc_id in self._df.index:
            yield self[dc_id]

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} ({len(self._df)} rows)>"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}:\n{repr(self._df)}"

    def __add__(self: T, other: T | T_LightDc) -> T:
        if isinstance(other, self.__class__):
            return self.__class__(pd.concat([self.df, other.df], axis=0))
        elif isinstance(other, self._get_dc_type()):
            other_frame = pd.DataFrame([other.to_simple_dict()]).set_index("id", drop=True)
            return self.__class__(pd.concat([self.df, other_frame], axis=0))
        else:
            raise TypeError(f"Cannot add {type(other)} to {type(self)}")

    def __len__(self) -> int:
        return len(self._df)

    def __eq__(self, other: "LdcRepo") -> bool:
        if not type(self) == type(other):
            return False
        return self.df.equals(other.df)

    def next_id(self) -> int:
        # Returns the next available id for a new item
        if len(self.df) == 0:
            return 1
        return max(self.df.index) + 1

    # GET
    def get_random(self) -> T_LightDc:
        if len(self) == 0:
            raise ValueError("Cannot get a random item from an empty repo")
        random_index = np.random.choice(self.df.index)
        return self[random_index]

    # UPDATE
    def add(self: T, x: T | T_LightDc) -> T:
        return self + x

    def update_frame(self: T, df: pd.DataFrame) -> T:
        return self.from_frame(df)

    @property
    def df(self) -> pd.DataFrame:
        return self._df.copy(deep=True)

    def _condition_to_logical_indexer(self, condition: Condition) -> pd.Series:
        filter_df = self.df
        filter_df["id"] = filter_df.index
        if callable(condition):
            return filter_df.apply(condition, axis=1)
        assert isinstance(condition, dict)
        condition = {k: simplify_type(x=v) for k, v in condition.items()}
        return filter_df[list(condition.keys())].eq(pd.Series(condition)).all(axis=1)

    def _filter(
        self,
        condition: Condition,
        operator: Operator,
        condition_2: Optional[Condition] = None,
    ) -> pd.Series:
        """
        :param condition: Either
        Fast and easy: A dictionary of key-value pairs to filter on
        OR
        Advanced: A function that is called on the underlying series
        Note that if a function is provided, the function is called on the underlying series which cannot contain
        complex types. Make sure to convert to simple types before using them in the function
        :param operator: "or", "and", "not" to combine two conditions or negate the first one
        :param condition_2: A second condition to combine with the first one
        :return: A logical indexer for the given condition or combination of conditions
        >>> self._filter({"bus": BusId(1), "color": Color.Red})
        >>> self._filter(lambda x: x["bus"] == 1 and x["color"] == simplify_type(Color.Red))
        >>>
        >>> self._filter({"bus": BusId(1)},"or",{"color": Color.Red})
        >>> self._filter(lambda x: x["bus"] == 1 or x["color"] == simplify_type(Color.Red))

        """
        if condition_2 is None:
            assert operator in ["not", None], f"Invalid operator for one condition: {operator}"
        else:
            assert operator in ["or", "and"], f"Invalid operator for two conditions: {operator}"

        if condition_2 is None:
            if operator == "not":
                return ~self._condition_to_logical_indexer(condition)
            else:
                return self._condition_to_logical_indexer(condition)

        if operator == "and":
            return self._condition_to_logical_indexer(condition) & self._condition_to_logical_indexer(condition_2)
        elif operator == "or":
            return self._condition_to_logical_indexer(condition) | self._condition_to_logical_indexer(condition_2)
        else:
            raise ValueError(f"Invalid operator {operator}")

    def filter(
        self: T,
        condition: Condition,
        operator: Operator = None,
        condition_2: Optional[Condition] = None,
    ) -> T:
        """
        Returns a copy of the repo filtered using the given condition
        :return: The filtered LdcFrame
        """
        logical_indexer = self._filter(condition=condition, operator=operator, condition_2=condition_2)
        filtered_df = self.df[logical_indexer]
        return self.__class__(filtered_df)

    def drop_items(
        self: T,
        condition: Condition,
        operator: Operator = None,
        condition_2: Optional[Condition] = None,
    ) -> T:
        """
        Returns a copy of the repo with elements deleted using the given condition
        :return: A new version of the LdcFrame with the items dropped
        """

        logical_indexer = self._filter(condition=condition, operator=operator, condition_2=condition_2)
        index = logical_indexer.loc[logical_indexer].index
        return self.from_frame(self.df.drop(index, axis=0))

    def drop_by_ids(self: T, ids: Iterable[int]) -> T:
        """
        :return: A copy of the repo with the elements with the given ids deleted
        """
        simple_ids = [simplify_type(x) for x in ids]
        return self.from_frame(self.df.drop(simple_ids, axis=0))

    def drop_one(self: T, item: int) -> T:
        return self.drop_by_ids([item])

    def as_objs(self) -> list[T_LightDc]:
        return list(self.__iter__())

    def to_simple_dict(self) -> dict[str, Any]:
        # Returns a dict representation of the frame
        return {
            "class": self.__class__.__name__,
            "data": [dc.to_simple_dict() for dc in self],
        }

    @classmethod
    def from_simple_dict(cls: type[T], data: dict) -> T:
        # Creates a frame from a dict representation
        assert data["class"] == cls.__name__, f"Class mismatch: {data['class']} != {cls.__name__}"
        dcs = [cls._get_dc_type().from_simple_dict(dc) for dc in data["data"]]
        return cls(dcs)

    @classmethod
    def from_frame(cls: type[T], df: pd.DataFrame) -> T:
        return cls(df)


T_LdcRepo = TypeVar("T_LdcRepo", bound=LdcRepo)
