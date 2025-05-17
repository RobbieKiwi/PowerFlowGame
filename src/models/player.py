from dataclasses import dataclass
from typing import Self, Callable

from src.models.data.ldc_repo import LdcRepo
from src.models.data.light_dc import LightDc
from src.models.ids import PlayerId


@dataclass(frozen=True)
class Player(LightDc):
    id: PlayerId
    name: str
    color: str
    money: float
    is_having_turn: bool  # Note that multiple players can have turns at the same time

    def __post_init__(self) -> None:
        assert (
            self.color.startswith("#")
            and len(self.color) == 7
            and int(self.color[1:], 16) < 0xFFFFFF
        ), "Invalid color format"


class PlayerRepo(LdcRepo[Player]):
    @classmethod
    def _get_dc_type(cls) -> type[Player]:
        return Player

    # GET
    @property
    def player_ids(self) -> list[PlayerId]:
        return [PlayerId(x) for x in self.df.index.tolist()]

    def get_player(self, player_id: PlayerId) -> Player:
        return self[player_id]

    def get_currently_playing(self) -> Self:
        return self.filter(condition={"is_having_turn": True})

    def are_all_players_finished(self) -> bool:
        return len(self.get_currently_playing()) == 0

    # UPDATE
    def _adjust_money(
        self, player_id: PlayerId, func: Callable[[float], float]
    ) -> Self:
        df = self.df
        df.loc[player_id, "money"] = func(df.loc[player_id, "money"])
        return self.update_frame(df)

    def add_money(self, player_id: PlayerId, amount: float) -> Self:
        # An example of how to mutate money
        return self._adjust_money(player_id, lambda x: x + amount)

    # DELETE
    def delete_player(self, player_id: PlayerId) -> Self:
        return self.drop_one(player_id)
