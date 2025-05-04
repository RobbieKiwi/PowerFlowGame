from dataclasses import dataclass
from typing import Self

from src.models.data.ldc_repo import LdcRepo
from src.models.data.light_dc import LightDc
from src.tools.typing import WrappedInt


class PlayerId(WrappedInt):
    @property
    def is_npc(self) -> bool:
        return self == PlayerId.get_npc()

    @classmethod
    def get_npc(cls) -> Self:  # noqa
        return cls(-1)



@dataclass(frozen=True)
class Player(LightDc):
    id: PlayerId
    name: str

class PlayerRepo(LdcRepo[Player]):
    @classmethod
    def _get_dc_type(cls) -> type[Player]:
        return Player

a = 2