import os
import socket
import threading
import tkinter as tk
import tkinter.scrolledtext as sct

server = socket.socket()                                            # Server's socket object for, well, being a server
clients = {}                                                        # dictionary of all clients connected to server
lt = None                                                           # variable for listening thread
rt = None                                                           # variable for response thread
ui = tk.Tk()                                                        # variable for holding and performing GUI operations
chatText = sct.ScrolledText(ui)                                     # variable for printing text ot the GUI window
lock = threading.Lock()                                             # lock for blocking other threads during critical procedures

class ListeningThread(threading.Thread):
    """A thread listening for new connections to the server"""

    def run(self):
        listen_and_connect()

class AddClientThread(threading.Thread):
    """A thread for handling new clients entering the chat room"""

    def __init__(self, conn, name = "new client"):
        threading.Thread.__init__(self, name = name)
        self.client = conn

    def run(self):
        add_client(self.client, self.name)

    def __str__(self):
        return self.name + "\n" + self.client

class ResponseThread(threading.Thread):
    """A thread for handling a client's messages"""

    def __init__(self, name):
        threading.Thread.__init__(self, name = name)

    def run(self):
            receive_message(self.name)

    def __str__(self):
        return self.name

def start_server(host = "localhost", port = 8888):
    """Create a server socket and start listening for connections"""
    printUI("Booting server...")
    try:
        server.bind((host, port))
        printUI("Server now running")
        lt = ListeningThread()
        lt.start()
    except socket.error as err:
        printUI("Failed to start server: " + str(err))
    chatText.pack(fil = tk.BOTH)

def listen_and_connect():
    """Listen for and accept incoming connections"""
    printUI("Listening for new clients...")
    try:
        while True:
            server.listen(5)
            conn, addr = server.accept()
            tempName = str(addr)
            act = AddClientThread(conn, tempName)
            act.start()
    except socket.error as err:
        printUI("Listening and connecting has failed:" + str(err))

def add_client(conn, name):
    """Ask the client for their username and, if not taken, add them to the chat room"""
    printUI("\nAdding new client " + name)
    try:
        while True:
            conn.send(str.encode("Enter username: "))
            printUI("Acquiring client's username")
            user = conn.recv(1024)
            user = user.decode()

            if user not in clients and user != "":
                lock.acquire()
                clients[user] = conn
                lock.release()
                rt = ResponseThread(user)                       # create new thread for the client
                rt.start()
                send_message("{0} has entered the chat room.".format(user))
                count()
                break
            else:
                invalid = "Username " + user + " is already taken."
                printUI(invalid)
                conn.send(str.encode(invalid))
    except ConnectionError:
        client_disconnect(name)

def receive_message(sender):
    """Receive messages from user"""
    printUI("Listening for responses from " + sender)
    try:
        while True:
            conn = clients[sender]
            text = conn.recv(1024)
            text = text.decode()
            if text != "":                                     # do not send an empty line if client enters nothing
                text = "{0}: {1}".format(sender, text)
                send_message(text)
    except ConnectionError:
        client_disconnect(sender)

def send_message(text):
    """Broadcast message to all users"""
    printUI("Brodcast message: " + text)
    text = str.encode(text)

    for user in clients:
        clients[user].send(text)

def remove_client(user):
    """Removes the given client from clients dict. and closes their connection"""
    lock.acquire()
    clients[user].close()
    del clients[user]
    lock.release()

def count():
    """Broadcast the current number of users in the room"""
    send_message(str(len(clients)) + " user(s) in the room.")

def client_disconnect(name = ""):
    """Handle abrupt client disconnections"""
    if name in clients:                                     # Runs when a ResponseThread exception is caught
        remove_client(name)
        printUI("Connection lost with " + name)
        send_message("{0} has left the room.".format(name))
        count()
    else:                                                   # Runs when a NewClientThread exception is caught
        printUI("Connection lost while adding " + name)

def printUI(text):
    """Print text onto the GUI widget, chatText (equivalent to print() for the chatText widget)"""
    chatText.insert(tk.INSERT, text + "\n")
    chatText.see(tk.END)                                    # focus on the last message printed (autoscroll)

def quit():
    """Close the server socket and exit the program"""
    server.close()
    ui.destroy()
    os._exit(0)

def init_GUI():
    """Initiate the GUI window and components"""
    # initialze GUI window properties
    ui.title("Server.py - I can hear all things...")
    ui.protocol("WM_DELETE_WINDOW", quit)
    ui.configure(bg = "white")
    ui.minsize(width = 550, height = 300)
    ui.grid_rowconfigure(0, weight = 1)                     # will allow GUI components in window to expand
    ui.grid_columnconfigure(0, weight = 1)                  # will allow GUI components in window to expand

    # initalize chatText with a scrollbar
    chatText.grid_columnconfigure(0, weight = 1)            # will allow GUI components in window to expand
    chatText.grid(sticky = tk.N + tk.S + tk.E + tk.W)       # expand in all directions if resized

def start_GUI():
    """Start the GUI program"""
    init_GUI()
    start_server()
    tk.mainloop()

start_GUI()
