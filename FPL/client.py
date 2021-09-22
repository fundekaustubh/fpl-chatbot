import socket
import asyncio
import aiohttp
from prettytable import PrettyTable
from fpl import FPL
import sys
from fpl import FPL
from fpl.utils import team_converter
from colorama import Fore, init

# Some global variables
HEADER = 64
PORT = 5050
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.137.1"
ADDR = (SERVER, PORT)
# initialise the server socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
# Function to send the message to the server
# encoding is used
def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b" " * (HEADER - len(send_length))  # padding with spaces
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))


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


async def captaincy_main(user_id):
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


async def fdr_main():
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


async def best_players_main():
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


while True:
    print("Here are your options:")
    print("1. Best players in the league so far.")
    print("2. Alternative fixture difficulty rating.")
    print("3. Optimal captain choice.")
    print("4. No more requests.")
    choice = int(input("Enter your choice: "))
    if choice <= 0 or choice > 4:
        print("Wrong choice!")
        break
    elif choice == 4:
        print("Okay!")
        break
    else:
        if choice == 1:
            asyncio.get_event_loop().run_until_complete(best_players_main())
        elif choice == 2:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(fdr_main())
        else:
            if sys.version_info >= (3, 7):
                # Python 3.7+
                asyncio.get_event_loop().run_until_complete(captaincy_main(1012012))
            else:
                # Python 3.6
                loop = asyncio.get_event_loop()
                loop.run_until_complete(main(1012012))
# send(f"{num1} {num2} {operation}")
send(DISCONNECT_MESSAGE)
print("\nDisconnected !")