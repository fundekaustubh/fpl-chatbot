import asyncio
from operator import attrgetter
import sys
import aiohttp
from prettytable import PrettyTable

from fpl import FPL
from fpl.utils import team_converter


def get_gameweek_score(player, gameweek):
    gameweek_history = next(
        history for history in player.history if history["round"] == gameweek
    )
    return gameweek_history["total_points"]


def get_gameweek_opponent(player, gameweek):
    gameweek_history = next(
        history for history in player.history if history["round"] == gameweek
    )
    return (
        f"{team_converter(gameweek_history['opponent_team'])} ("
        f"{'H' if gameweek_history['was_home'] else 'A'})"
    )


def get_point_difference(player_a, player_b, gameweek):
    if player_a == player_b:
        return 0

    history_a = next(
        history for history in player_a.history if history["round"] == gameweek
    )
    history_b = next(
        history for history in player_b.history if history["round"] == gameweek
    )

    return history_a["total_points"] - history_b["total_points"]


async def main(user_id):
    player_table = PrettyTable()
    player_table.field_names = ["Gameweek", "Captain", "Top scorer", "Δ"]
    player_table.align = "r"
    total_difference = 0

    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        user = await fpl.get_user(user_id)
        picks = await user.get_picks()
        gameweeks = []
        for key in picks.keys():
            gameweeks.append(picks[key])
        for i, elements in enumerate(gameweeks):
            gameweek = i + 1
            captain_id = next(player for player in elements if player["is_captain"])[
                "element"
            ]
            players = await fpl.get_players(
                [player["element"] for player in elements], include_summary=True
            )

            captain = next(player for player in players if player.id == captain_id)

            top_scorer = max(players, key=lambda x: get_gameweek_score(x, gameweek))

            point_difference = get_point_difference(captain, top_scorer, gameweek)

            player_table.add_row(
                [
                    gameweek,
                    (
                        f"{captain.web_name} - "
                        f"{get_gameweek_score(captain, gameweek)} points vs. "
                        f"{get_gameweek_opponent(captain, gameweek)}"
                    ),
                    (
                        f"{top_scorer.web_name} - "
                        f"{get_gameweek_score(top_scorer, gameweek)} points vs. "
                        f"{get_gameweek_opponent(top_scorer, gameweek)}"
                    ),
                    point_difference,
                ]
            )

            total_difference += point_difference

    print(player_table)
    print(f"Total point difference is {abs(total_difference)} points!")


if __name__ == "__main__":
    if sys.version_info >= (3, 7):
        # Python 3.7+
        asyncio.get_event_loop().run_until_complete(main(1012012))
    else:
        # Python 3.6
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(1012012))
