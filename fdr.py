import asyncio
import aiohttp
import sys
from colorama import Fore, init
from prettytable import PrettyTable

from fpl import FPL


async def main():
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


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
