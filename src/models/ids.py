from typing import Self

from src.tools.typing import WrappedInt


class PlayerId(WrappedInt):
    @property
    def is_npc(self) -> bool:
        return self == PlayerId.get_npc()

    @classmethod
    def get_npc(cls) -> Self:  # noqa
        return cls(-1)


class AssetId(WrappedInt):
    pass


class BusId(WrappedInt):
    pass


class TransmissionId(WrappedInt):
    pass
