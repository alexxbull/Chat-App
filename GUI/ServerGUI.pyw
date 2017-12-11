import os
import socket
import threading
import tkinter as tk
import tkinter.scrolledtext as sct

server = socket.socket()                                                                                # Server's socket object for, well, being a server
clients = {}                                                                                            # dictionary of all clients connected to server
ui = tk.Tk()                                                                                            # variable for holding and performing GUI operations
chatText = sct.ScrolledText(ui)                                                                         # variable for printing text ot the GUI window

def start_server(host = "localhost", port = 8888):
    "Create a server socket and start listening for connections"
    printUI("Booting server...")
    try:
        server.bind((host, port))
        printUI("Server now running")
        lct = threading.Thread(target = listen_and_connect)                                             # make new thread for server for new clients
        lct.start()
    except socket.error as err:
        printUI("Failed to start server: " + str(err))
    chatText.pack(fill = tk.BOTH)

def listen_and_connect():
    "Listen for and accept incoming connections"
    printUI("Listening for new clients...")
    try:
        while True:
            server.listen(5)
            conn, addr = server.accept()
            tempName = str(addr)
            nct = threading.Thread(target = add_client, args = (conn, tempName), name = tempName)       # make new thread for handling the new client
            nct.start()
    except socket.error as err:
        printUI("Listening and connecting has failed:" + str(err))

def add_client(conn, name):
    "Ask the client for their username and, if not taken, add them to the chat room"
    printUI("\nAdding new client " + name)
    try:
        printUI("Acquiring username for " + name)                                                       # temporary formating fix, this will run again in while loop if connection is lost
        while True:
            conn.send(str.encode("Enter username: "))
            user = conn.recv(1024)
            user = user.decode()

            if user not in clients and user != "":
                clients[user] = conn
                send_message("{0} has entered the chat room.".format(user))
                count()
                receive_message(user)
                break
            elif user in clients:
                invalid = "Username " + user + " is already taken."
                printUI(invalid)
                conn.send(str.encode(invalid))
    except ConnectionError:
        client_disconnect(name)

def receive_message(sender):
    "Receive messages from user"
    printUI("Listening for responses from " + sender)
    try:
        while True:
            conn = clients[sender]
            text = conn.recv(1024)
            text = text.decode()
            if text != "":                                                                              # do not send an empty line if client enters nothing
                text = "{0}: {1}".format(sender, text)
                send_message(text)
    except ConnectionError:
        client_disconnect(sender)

def send_message(text):
    "Broadcast message to all users"
    printUI("Brodcast message: " + text)
    text = str.encode(text)
    for user in clients:
        clients[user].send(text)

def count():
    "Broadcast the current number of users in the room"
    send_message(str(len(clients)) + " user(s) in the room.")

def client_disconnect(name = ""):
    "Handle (abrupt) client disconnections"
    if name in clients:
        clients[name].close()
        del clients[name]
        printUI("Connection lost with " + name)
        send_message("{0} has left the room.".format(name))
        count()
    else:                                                                                               # Runs when a NewClientThread exception is caught
        printUI("Connection lost while adding " + name)

def printUI(text):
    "Print text onto the GUI widget, chatText (equivalent to print() for the chatText widget)"
    chatText.insert(tk.END, text + "\n")
    chatText.see(tk.END)                                                                                # focus on the last message printed (autoscroll)

def quit():
    "Close the server socket and exit the program"
    server.close()
    ui.destroy()
    os._exit(0)

def init_GUI():
    "Initiate the GUI window and components"
    # initialze GUI window properties
    ui.title("Server.py - I can hear all things...")
    ui.protocol("WM_DELETE_WINDOW", quit)
    ui.configure(bg = "white")
    ui.minsize(width = 550, height = 300)
    ui.grid_rowconfigure(0, weight = 1)                                                                 # will allow GUI components in window to expand
    ui.grid_columnconfigure(0, weight = 1)                                                              # will allow GUI components in window to expand

    # initalize chatText with a scrollbar
    chatText.grid_columnconfigure(0, weight = 1)                                                        # will allow GUI components in window to expand
    chatText.grid(sticky = tk.N + tk.S + tk.E + tk.W)                                                   # expand in all directions if resized

def start_GUI():
    "Start the GUI program"
    init_GUI()
    start_server()
    tk.mainloop()

start_GUI()


"""
Active Threads:
- Main thread will handle the GUI
- A new thread (lct) will handle listening for new connections/clients
- A new thread (nct) is made for interacting with clients
"""
