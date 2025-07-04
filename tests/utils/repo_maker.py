from abc import abstractmethod
from itertools import count
from typing import Generic, Self, Literal, Optional, TypeVar

import numpy as np

from src.models.assets import AssetRepo, AssetInfo, AssetType
from src.models.buses import Bus, BusRepo
from src.models.colors import Color
from src.models.data.ldc_repo import T_LdcRepo
from src.models.data.light_dc import T_LightDc
from src.models.ids import PlayerId, AssetId, BusId, TransmissionId
from src.models.player import PlayerRepo, Player
from src.models.transmission import TransmissionRepo, TransmissionInfo
from tests.utils.random_choice import random_choice, random_choice_multi


T_RepoMaker = TypeVar("T_RepoMaker", bound="RepoMaker")


class RepoMaker(Generic[T_LdcRepo, T_LightDc]):
    def __init__(self, *args, **kwargs) -> None:
        self.dcs: list[T_LightDc] = []
        self.id_counter = count(start=0)

    @abstractmethod
    def _get_repo_type(self) -> type[T_LdcRepo]:
        pass

    @abstractmethod
    def _make_dc(self, *args, **kwargs) -> T_LightDc:
        pass

    def _pre_make_hook(self) -> None:
        pass

    def __add__(self: T_RepoMaker, dc: T_LightDc | list[T_LightDc]) -> T_RepoMaker:
        if isinstance(dc, list):
            self.dcs.extend(dc)
        else:
            self.dcs.append(dc)
        return self

    def add_n_random(self: T_RepoMaker, n: int) -> T_RepoMaker:
        new_dcs = [self._make_dc() for _ in range(n)]
        self.dcs.extend(new_dcs)
        return self

    def make(self) -> T_LdcRepo:
        self._pre_make_hook()
        return self._get_repo_type()(dcs=self.dcs)


class BusRepoMaker(RepoMaker[BusRepo, Bus]):
    @classmethod
    def make_quick(cls, n_npc_buses: int = 10, player_ids: Optional[list[PlayerId]] = None) -> BusRepo:
        return cls(player_ids=player_ids).add_n_random(n_npc_buses).make()

    def __init__(self, player_ids: Optional[list[PlayerId]] = None) -> None:
        super().__init__()
        if player_ids is None:
            player_ids = [PlayerId(i) for i in range(3)]
        self.player_ids = player_ids

    def add_bus(self, player_id: PlayerId = PlayerId.get_npc()) -> Self:
        """Add a bus for a specific player."""
        self.dcs.append(self._make_dc(player_id=player_id))
        return self

    def _make_dc(self, player_id: PlayerId = PlayerId.get_npc()) -> Bus:

        map_width: float = 20.0
        half_width = map_width / 2

        centre_x, centre_y = self._get_current_centre()

        def centre_rand() -> float:
            """Generate a random number between -0.5 and 0.5."""
            return 2 * (np.random.rand() - 0.5)

        x = -centre_x + abs(half_width - centre_x) * centre_rand()
        y = -centre_y + abs(half_width - centre_y) * centre_rand()

        bus_id = next(self.id_counter)
        return Bus(
            id=BusId(bus_id),
            x=x,
            y=y,
            player_id=player_id,
        )

    def _get_current_centre(self) -> tuple[float, float]:
        """Get the current centre of the buses."""
        if not self.dcs:
            return 0.0, 0.0
        x_coords = [bus.x for bus in self.dcs]
        y_coords = [bus.y for bus in self.dcs]
        return float(np.mean(x_coords)), float(np.mean(y_coords))

    def _get_repo_type(self) -> type[BusRepo]:
        return BusRepo

    def _pre_make_hook(self) -> None:
        # Ensure that there is exactly one bus per non-npc player
        player_ids_with_buses = {bus.player_id for bus in self.dcs if bus.player_id != PlayerId.get_npc()}
        players_without_buses = set(self.player_ids) - player_ids_with_buses

        for player_id in players_without_buses:
            self.dcs.append(self._make_dc(player_id=player_id))


class PlayerRepoMaker(RepoMaker[PlayerRepo, Player]):
    @classmethod
    def make_quick(cls, n: int = 3) -> PlayerRepo:
        maker = cls()
        return maker.add_n_random(n).make()

    def _make_dc(self) -> Player:
        player_id = next(self.id_counter)
        hue = np.random.randint(0, 255)
        saturation = np.random.randint(200, 255)
        value = 200

        color = Color(x=(hue, saturation, value), color_model="hsv")
        return Player(
            id=PlayerId(player_id),
            name=f"Player {player_id}",
            color=color,
            money=float(np.random.rand() * 100),  # Just an example of money
            is_having_turn=False,
        )

    def _get_repo_type(self) -> type[PlayerRepo]:
        return PlayerRepo

    def _pre_make_hook(self) -> None:
        # Ensure that there is exactly one bus per non-npc player
        player_ids = [dc.id for dc in self.dcs]
        if PlayerId.get_npc() not in player_ids:
            self.dcs.append(
                Player(id=PlayerId.get_npc(), name="NPC", color=Color("black"), money=0.0, is_having_turn=False)
            )


class AssetRepoMaker(RepoMaker[AssetRepo, AssetInfo]):
    @classmethod
    def make_quick(
        cls, n_normal_assets: int = 3, player_ids: Optional[list[PlayerId]] = None, bus_repo: Optional[BusRepo] = None
    ) -> AssetRepo:
        return (
            cls(player_ids=player_ids, bus_repo=bus_repo)
            .add_n_random(n_normal_assets)
            .add_asset(owner=PlayerId.get_npc(), is_for_sale=True)
            .make()
        )

    def __init__(self, player_ids: Optional[list[PlayerId]] = None, bus_repo: Optional[BusRepo] = None) -> None:
        super().__init__()
        if player_ids is None:
            player_ids = [PlayerId(i) for i in range(3)]

        if bus_repo is None:
            bus_repo = BusRepoMaker.make_quick(player_ids=player_ids)
        self.player_ids = player_ids
        self._bus_repo = bus_repo

    def add_assets_to_buses(self, buses: list[BusId]) -> Self:
        """Add assets to specific buses."""
        for bus in buses:
            self.dcs.append(self._make_dc(bus=bus))
        return self

    def add_asset(
        self,
        asset: Optional[AssetInfo] = None,
        cat: Optional[Literal["Generator", "Load", "IceCream"]] = None,
        owner: Optional[PlayerId] = None,
        bus: Optional[BusId] = None,
        power_std: Optional[float] = None,
        is_for_sale: Optional[bool] = None,
    ) -> Self:
        if asset is not None:
            for x in [cat, owner, bus]:
                assert x is None, "Cannot specify asset and any of cat, owner, or bus at the same time"
            self.dcs.append(asset)
            return self

        dc = self._make_dc(cat=cat, owner=owner, bus=bus, power_std=power_std, is_for_sale=is_for_sale)
        self.dcs.append(dc)
        return self

    def _get_random_player_id(self) -> PlayerId:
        return random_choice(self.player_ids) if random_choice([True, False]) else PlayerId.get_npc()

    def _get_random_bus_id(self) -> BusId:
        return random_choice(self._bus_repo.bus_ids)

    def _make_dc(
        self,
        cat: Optional[Literal["Generator", "Load", "IceCream"]] = None,
        owner: Optional[PlayerId] = None,
        bus: Optional[BusId] = None,
        power_std: Optional[float] = None,
        is_for_sale: Optional[bool] = None,
    ) -> AssetInfo:
        asset_id = next(self.id_counter)

        if cat is None:
            cat = random_choice(["Generator", "Load"])

        if owner is None:
            owner = self._get_random_player_id()

        if bus is None:
            bus = self._get_random_bus_id()

        if power_std is None:
            power_std = float(np.random.rand() * 10)

        if is_for_sale is None:
            is_for_sale = random_choice([True, False]) if owner is PlayerId.get_npc() else False

        asset_type: AssetType = {
            "Generator": AssetType.GENERATOR,
            "Load": AssetType.LOAD,
            "IceCream": AssetType.LOAD,  # Ice cream is a special type of load
        }[cat]
        is_icecream = cat == "IceCream"
        offset = {"Generator": 0, "Load": 200, "IceCream": 500}[cat]

        marginal_cost = float(np.random.rand() * 50) + offset
        if asset_type == AssetType.GENERATOR:
            bid_price = marginal_cost + float(np.random.rand() * 50)
        else:
            bid_price = marginal_cost - float(np.random.rand() * 50)

        return AssetInfo(
            id=AssetId(asset_id),
            owner_player=owner,
            asset_type=asset_type,
            bus=bus,
            power_expected=float(np.random.rand() * 100),
            power_std=power_std,
            is_for_sale=is_for_sale,
            minimum_acquisition_price=float(np.random.rand() * 1000),
            fixed_operating_cost=float(np.random.rand() * 100),
            marginal_cost=marginal_cost,
            bid_price=bid_price,
            is_ice_cream=is_icecream,
            is_active=np.random.rand() > 0.2,
        )

    def _get_repo_type(self) -> type[AssetRepo]:
        return AssetRepo

    def _pre_make_hook(self) -> None:
        for bus in self._bus_repo.ice_cream_buses:
            self.dcs.append(self._make_dc(cat="IceCream", bus=bus.id, owner=bus.player_id))


class TransmissionRepoMaker(RepoMaker[TransmissionRepo, TransmissionInfo]):
    @classmethod
    def make_quick(
        cls, n: int = 10, player_ids: Optional[list[PlayerId]] = None, bus_ids: Optional[list[BusId]] = None
    ) -> TransmissionRepo:
        maker = cls(player_ids=player_ids, bus_ids=bus_ids)
        return maker.add_n_random(n).make()

    def __init__(self, player_ids: Optional[list[PlayerId]] = None, bus_ids: Optional[list[BusId]] = None) -> None:
        super().__init__()
        if player_ids is None:
            player_ids = [PlayerId(i) for i in range(3)]
        if bus_ids is None:
            bus_ids = [BusId(i) for i in range(5)]
        self.player_ids = player_ids
        self.bus_ids = bus_ids

    def _get_random_player_id(self) -> PlayerId:
        return random_choice(self.player_ids) if random_choice([True, False]) else PlayerId.get_npc()

    def _get_random_bus_pair(self) -> tuple[BusId, BusId]:
        bus1, bus2 = random_choice_multi(x=self.bus_ids, size=2, replace=False)
        return min(bus1, bus2), max(bus1, bus2)

    def _make_dc(
        self, owner: Optional[PlayerId] = None, buses: Optional[tuple[BusId, BusId]] = None
    ) -> TransmissionInfo:
        transmission_id = TransmissionId(next(self.id_counter))
        if owner is None:
            owner = self._get_random_player_id()
        if buses is None:
            buses = self._get_random_bus_pair()
        bus1, bus2 = buses
        return TransmissionInfo(
            id=transmission_id,
            owner_player=owner,
            bus1=bus1,
            bus2=bus2,
            reactance=float(np.random.rand() * 10 + 1),
            capacity=float(np.random.rand() * 100 + 50),
            health=int(np.random.randint(1, 6)),
            fixed_operating_cost=float(np.random.rand() * 100),
            is_for_sale=random_choice([True, False]),
            minimum_acquisition_price=float(np.random.rand() * 1000) if random_choice([True, False]) else 0.0,
            is_active=np.random.rand() > 0.2,
        )

    def _get_repo_type(self) -> type[TransmissionRepo]:
        return TransmissionRepo

    def _pre_make_hook(self) -> None:
        # Connect islands before making the repo
        mentioned_buses = {t.bus1 for t in self.dcs} | {t.bus2 for t in self.dcs}
        islanded_buses = [bus for bus in self.bus_ids if bus not in mentioned_buses]

        for i_bus in islanded_buses:
            other_bus = random_choice([b for b in self.bus_ids if b != i_bus])
            bus1 = min(i_bus, other_bus)
            bus2 = max(i_bus, other_bus)
            self.dcs.append(self._make_dc(owner=self._get_random_player_id(), buses=(bus1, bus2)))
