import socket
import threading
import sys
import time

server = socket.socket()                                                                        # Server's socket object for, well, being a server
clients = {}                                                                                    # dictionary of all clients connected to server

def start_server(host = "localhost", port = 8888):
    "Create a server socket and start listening for connections"
    print("Booting server...")
    try:
        server.bind((host, port))
        print("Server now running")
        listen_and_connect()
    except socket.error as err:
        print("Failed to start server:")
        print(str(err) + "\nExiting...")
        time.sleep(2)
        sys.exit(1)

def listen_and_connect():
    "Listen for and accept incoming connections"
    print("Listening for new clients...")
    try:
        while True:
            server.listen(5)
            conn, addr = server.accept()
            tempName = str(addr)
            nct = threading.Thread(target = add_client, args = (conn, tempName), name = tempName)   # make new thread for handling the new client
            nct.start()
    except socket.error as err:
        print("Listening and connecting has failed:")
        print(str(err) + "\nExiting...")
        time.sleep(2)
        sys.exit(1)

def add_client(conn, tempName):
    "Ask the client for their username and, if not taken, add them to the chat room"
    print("\nAdding new client", tempName)
    try:
        while True:
            print("Acquiring username for", tempName)
            conn.send(str.encode("Enter a username: "))
            user = conn.recv(1024)
            user = user.decode()

            if user not in clients and user != "":
                clients[user] = conn
                system_message("{0} has entered the chat room.".format(user))
                count()
                receive_message(user)
                break
            elif user in clients:
                invalid = "Username " + user + " is already taken."
                print(invalid)
                conn.send(str.encode(invalid))
    except (ConnectionResetError, ConnectionAbortedError):
        client_disconnect(tempName)

def receive_message(sender):
    "Receive messages from user"
    print("Listening for responses from", sender)
    try:
        while True:
            conn = clients[sender]
            text = conn.recv(1024)
            text = text.decode()

            if text.lower() == "exit":
                goodbye = str.encode("You have left the chat room. Goodbye!")
                conn.send(goodbye)
                remove_client(sender)
                text = "{0} has left the room.".format(sender)
                system_message(text)
                count()
                break
            else:
                send_message(sender, text)
    except (ConnectionResetError, ConnectionAbortedError):
        client_disconnect(sender)

def send_message(sender, text):
    "Forward message from sender to all users"
    print(sender + " says:", text)
    text = "{0}: {1}".format(sender, text)
    text = str.encode(text)

    for user in [user for user in clients if user != sender]:
        clients[user].send(text)

def system_message(text):
    "Broadcast message to all users"
    print("Brodcast message:", text)
    text = str.encode(text)

    for user in clients:
        clients[user].send(text)

def remove_client(user):
    "Removes the given client from clients dict. and closes their connection"
    clients[user].close()
    del clients[user]

def count():
    "Broadcast the current number of users in the room"
    system_message(str(len(clients)) + " user(s) in the room.")
    print()

def client_disconnect(name = ""):
    "Handle (abrupt) client disconnections"
    if name in clients:                                                                             # Runs when a response thread exception is caught
        remove_client(name)
        print("Connection lost with", name)
        system_message("{0} has left the room.".format(name))
        count()
    else:                                                                                           # Runs when adding new client thread exception is caught
        print("Connection lost while adding", name)

start_server()

"""
Active Threads:
- Main thread will handle listening for new connections/clients
- A new thread (nct) is made for interacting with clients
"""
