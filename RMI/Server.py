import Pyro4
import random
import os
import datetime
import subprocess
import socket
import asyncio
import aiohttp
from prettytable import PrettyTable
from fpl import FPL
import sys
from fpl import FPL
from fpl.utils import team_converter
from colorama import Fore, init

now = datetime.datetime.now()
print(f"Date: {now.strftime('%d - %m - %y')}")
print(f"Time: {now.strftime('%H:%M:%S')}")


@Pyro4.expose
class Server(object):
    def get_usid(self, name):
        return "Hello, {0}.\n" "Your Current User Session is {1}:".format(
            name, random.randint(0, 1000000)
        )

    def get_gameweek_score(self, player, gameweek):
        gameweek_history = next(
            history for history in player.history if history["round"] == gameweek
        )
        return gameweek_history["total_points"]

    def get_gameweek_opponent(self, player, gameweek):
        gameweek_history = next(
            history for history in player.history if history["round"] == gameweek
        )
        return (
            f"{team_converter(gameweek_history['opponent_team'])} ("
            f"{'H' if gameweek_history['was_home'] else 'A'})"
        )

    def get_point_difference(self, player_a, player_b, gameweek):
        if player_a == player_b:
            return 0

        history_a = next(
            history for history in player_a.history if history["round"] == gameweek
        )
        history_b = next(
            history for history in player_b.history if history["round"] == gameweek
        )

        return history_a["total_points"] - history_b["total_points"]

    async def captaincy_main(self, user_id):
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
                captain_id = next(
                    player for player in elements if player["is_captain"]
                )["element"]
                players = await fpl.get_players(
                    [player["element"] for player in elements], include_summary=True
                )

                captain = next(player for player in players if player.id == captain_id)

                top_scorer = max(
                    players, key=lambda x: self.get_gameweek_score(x, gameweek)
                )

                point_difference = self.get_point_difference(
                    captain, top_scorer, gameweek
                )

                player_table.add_row(
                    [
                        gameweek,
                        (
                            f"{captain.web_name} - "
                            f"{self.get_gameweek_score(captain, gameweek)} points vs. "
                            f"{self.get_gameweek_opponent(captain, gameweek)}"
                        ),
                        (
                            f"{top_scorer.web_name} - "
                            f"{self.get_gameweek_score(top_scorer, gameweek)} points vs. "
                            f"{self.get_gameweek_opponent(top_scorer, gameweek)}"
                        ),
                        point_difference,
                    ]
                )

                total_difference += point_difference

        print(player_table)
        print(f"Total point difference is {abs(total_difference)} points!")

    async def fdr_main(self):
        async with aiohttp.ClientSession() as session:
            fpl = FPL(session)
            fdr = await fpl.FDR()

        fdr_table = PrettyTable()
        fdr_table.field_names = [
            "Team",
            "All (H)",
            "All (A)",
            "GK (H)",
            "GK (A)",
            "DEF (H)",
            "DEF (A)",
            "MID (H)",
            "MID (A)",
            "FWD (H)",
            "FWD (A)",
        ]

        for team, positions in fdr.items():
            row = [team]
            for difficulties in positions.values():
                for location in ["H", "A"]:
                    if difficulties[location] == 5.0:
                        row.append(Fore.RED + "5.0" + Fore.RESET)
                    elif difficulties[location] == 1.0:
                        row.append(Fore.GREEN + "1.0" + Fore.RESET)
                    else:
                        row.append(f"{difficulties[location]:.2f}")

            fdr_table.add_row(row)

        fdr_table.align["Team"] = "l"
        print(fdr_table)

    async def best_players_main(self):
        async with aiohttp.ClientSession() as session:
            fpl = FPL(session)
            players = await fpl.get_players()

        top_performers = sorted(
            players, key=lambda x: x.goals_scored + x.assists, reverse=True
        )

        player_table = PrettyTable()
        player_table.field_names = ["Player", "£", "G", "A", "G + A"]
        player_table.align["Player"] = "l"

        for player in top_performers[:40]:
            goals = player.goals_scored
            assists = player.assists
            player_table.add_row(
                [
                    player.web_name,
                    f"£{player.now_cost / 10}",
                    goals,
                    assists,
                    goals + assists,
                ]
            )

        print(player_table)


daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
url = daemon.register(Server)
ns.register("RMI.calculator", url)
print(
    "The server is now active, please request your calculations or start file transfer."
)
daemon.requestLoop()