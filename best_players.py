import asyncio
import sys
import aiohttp
from prettytable import PrettyTable

from fpl import FPL


async def main():
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        players = await fpl.get_players()

    top_performers = sorted(
        players, key=lambda x: x.goals_scored + x.assists, reverse=True
    )

    player_table = PrettyTable()
    player_table.field_names = ["Player", "£", "G", "A", "G + A"]
    player_table.align["Player"] = "l"

    for player in top_performers[:10]:
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


if __name__ == "__main__":
    if sys.version_info >= (3, 7):
        # Python 3.7+
        asyncio.run(main())
    else:
        # Python 3.6
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())