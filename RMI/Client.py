import Pyro4
import os
import datetime
import socket
import asyncio
import aiohttp
from prettytable import PrettyTable
from fpl import FPL
import sys
from fpl import FPL
from fpl.utils import team_converter
from colorama import Fore, init

Client = Pyro4.Proxy("PYRONAME:RMI.calculator")
name = input("What is your name? Enter: ").strip()

now = datetime.datetime.now()
print(f"Date: {now.strftime('%d - %m - %y')}")
print(f"Time: {now.strftime('%H:%M:%S')}")
print(Client.get_usid(name))
# print("Enter the number of calculations to be done: ")
# n = int(input("Enter n: "))
# while n > 0:
#     n -= 1
#     a = int(input("Enter a: "))
#     b = int(input("Enter b: "))
#     print("Enter the choice for calculations:")
#     print("1. Add")
#     print("2. Subtract")
#     print("3. Multiply")
#     print("4. Divide")
#     print("5. Power")
#     c = int(input("Enter choice: "))
#     if c == 1:
#         print(Client.add(a, b))
#     elif c == 2:
#         print(Client.subtract(a, b))
#     elif c == 3:
#         print(Client.multiply(a, b))
#     elif c == 4:
#         print(Client.division(a, b))
#     elif c == 5:
#         print(Client.exp(a, b))
#     else:
#         print("Invalid input")
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
            asyncio.get_event_loop().run_until_complete(Client.best_players_main())
        elif choice == 2:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(Client.fdr_main())
        else:
            if sys.version_info >= (3, 7):
                # Python 3.7+
                asyncio.get_event_loop().run_until_complete(
                    Client.captaincy_main(1012012)
                )
            else:
                # Python 3.6
                loop = asyncio.get_event_loop()
                loop.run_until_complete(main(1012012))