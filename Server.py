import socket
import threading
import sys

server = socket.socket()
clients = {}
lt = None       #variable for listening thread
rt = None       #variable for response thread

class ListeningThread(threading.Thread):
    """A thread listening for new connections to the server"""

    def run(self):
        print("Listening for new clients...")
        listen_and_connect()

class AddClientThread(threading.Thread):
    """A thread for handling new clients entering the chat room"""

    def __init__(self, conn, name = "new client"):
        threading.Thread.__init__(self, name = name)
        self.client = conn

    def run(self):
        print("\nAdding new client", self.name)
        try:
            add_client(self.client)
        except ConnectionResetError:
            client_disconnect(self.name)

class ResponseThread(threading.Thread):
    """A thread for handling a client's messages"""

    def __init__(self, name):
        threading.Thread.__init__(self, name = name)

    def run(self):
        try:
            print("Listening for responses from", self.name)
            receive_message(self.name)
        except ConnectionResetError:
            client_disconnect(self.name)

    def __str__(self):
        return self.name

def start_server(host = "localhost", port = 8888):
    """Create a server socket and start listening for connections"""
    print("Booting server...")
    global server, clients, lt
    try:
        server.bind((host, port))
        print("Server now running")
        lt = ListeningThread()
        lt.start()
    except socket.error as err:
        print("Failed to start server:\n", str(err))
        sys.exit(1)

def listen_and_connect():
    """Listen for and accept incoming connections"""
    global server, clients, lt, rt
    try:
        while True:
            server.listen(5)
            conn, addr = server.accept()
            tempName = str(addr)
            act = AddClientThread(conn, tempName)
            act.start()
    except socket.error as err:
        print("Listening and connecting has failed:\n", str(err))
        sys.exit(1)

def add_client(conn):
    """Ask the client for their username and, if not taken, add them to the chat room"""
    global clients
    while True:
        conn.send(str.encode("Enter a username: "))
        print("Acquiring client's username")
        user = conn.recv(1024)
        user = user.decode()

        if user not in clients:
            clients[user] = conn
            rt = ResponseThread(user) # create new thread for the client
            rt.start()
            system_message("{0} has entered the chat room.".format(user))
            count()
            break
        else:
            invalid = "Username " + user + " is already taken."
            print(invalid)
            conn.send(str.encode(invalid))

def receive_message(sender):
    """Receive messages from user"""
    while True:
        global clients
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

def send_message(sender, text):
    """Forward message from sender to all users"""
    print(sender + " says:", text)
    text = "{0}: {1}".format(sender, text)
    text = str.encode(text)

    global clients
    for user in [user for user in clients if user != sender]:
        clients[user].send(text)

def system_message(text):
    """Broadcast message to all users"""
    print("Brodcast message:", text)
    text = str.encode(text)

    global clients
    for user in clients:
        clients[user].send(text)

def remove_client(user):
    """Removes the given client from clients dict. and closes their connection"""
    global clients
    clients[user].close()
    del clients[user]

def count():
    """Broadcast the current number of users in the room"""
    system_message(str(len(clients)) + " user(s) in the room.")
    print()

def client_disconnect(name = ""):
    if name in clients: # Runs when a ResponseThread exception is caught
        remove_client(name)
        print("Connection lost with", name)
        system_message("{0} has left the room.".format(name))
        count()
    else:   # Runs when a NewClientThread exception is caught
        print("Connection lost while adding", name)

def main():
    start_server()

main()
