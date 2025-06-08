from src.app.simple_front_end.joystick import Joystick
from src.models.message import *  # noqa

if __name__ == "__main__":
    # To play, run this script in the REPL and use the joystick to interact with the game
    joystick = Joystick(game_id_or_players=["Alice", "Bob"])
    print(joystick.latest_game_state)
