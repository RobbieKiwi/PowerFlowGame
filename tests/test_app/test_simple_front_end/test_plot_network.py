from unittest import TestCase

from src.app.simple_front_end.plotting.grid_plotter import GridPlotter
from tests.utils.game_state_maker import GameStateMaker
from tests.utils.repo_maker import BusRepoMaker, TransmissionRepoMaker, PlayerRepoMaker


class TestPlotNetwork(TestCase):
    def test_plot_network(self) -> None:
        # This is a placeholder for the actual test implementation.
        # The test should verify that the plot_network function works as expected.

        player_repo = PlayerRepoMaker.make_quick()
        bus_repo = BusRepoMaker.make_quick(n_npc_buses=0)
        transmission_repo = TransmissionRepoMaker.make_quick(
            player_ids=player_repo.player_ids, bus_ids=bus_repo.bus_ids, n=2
        )
        game_state = (
            GameStateMaker()
            .add_player_repo(player_repo=player_repo)
            .add_bus_repo(bus_repo=bus_repo)
            .add_transmission_repo(transmission_repo=transmission_repo)
            .make()
        )
        GridPlotter().plot(game_state=game_state)
