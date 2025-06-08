from unittest import TestCase

from src.app.simple_front_end.plot_network import GridPlotter
from tests.utils.game_state_maker import GameStateMaker


class TestPlotNetwork(TestCase):
    def test_plot_network(self) -> None:
        # This is a placeholder for the actual test implementation.
        # The test should verify that the plot_network function works as expected.

        game_state = GameStateMaker().make()
        GridPlotter.plot(game_state=game_state)
