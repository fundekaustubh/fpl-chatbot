import socket

# import asyncio

# import aiohttp
# from prettytable import PrettyTable

# from fpl import FPL

# players = []
# fdr = []

# Some global variables
HEADER = 64
PORT = 5050
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.29.14"
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


num1 = int(input("Enter number1: "))
num2 = int(input("Enter number2: "))
print("The operations allowed are: ", "\n1) Add 2) Subtract 3) Multiply 4) Divide\n")
operation = int(input("Enter the operation number here: "))
if operation == 1:
    ans = num1 + num2
elif operation == 2:
    ans = num1 - num2
elif operation == 3:
    ans = num1 * num2
elif operation == 4:
    ans = num1 / num2
print("Answer: ", ans)

send(f"{num1} {num2} {operation}")

send(DISCONNECT_MESSAGE)
print("\n Disconnected !")
