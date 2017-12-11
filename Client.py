import os
import socket
import threading
import time

client = socket.socket()                                                            # Client's socket object for, well, being a client

def join_server(h = "localhost", p = 8888):
    "Connect client to server"
    try:
        host = h
        post = p
        client.connect((host, post));
    except socket.error as err:
        print("Failed to connect to server.")
        print(str(err) + "\nExiting...")
        time.sleep(2)
        quit()
    else:
        send_username()

def send_username():
    "Complete username registration and then enter chat room"
    try:
        while True:
            getName = client.recv(1024)                                             # read server message for entering username
            getName = getName.decode()
            name = input(getName)

            client.send(str.encode(name))                                           # send server the username entered
            valid = client.recv(1024)                                               # check if server approves of name
            valid = valid.decode()
            taken = "Username " + name + " is already taken."
            if valid == taken:
                print(taken)
                continue
            elif valid != taken and name != "":
                rt = threading.Thread(target = receive_message, name = name)        # make a new thread for receiving messages from the sever
                rt.start()
                send_message()                                                      # sending messages to server will be handled in the main thread
                break
    except socket.error as err:
        print("Lost connection with server.\nExiting...")
        time.sleep(2)
        quit()

def receive_message():
    "Listen for messages from the server and display them."
    try:
        while True:
            text = client.recv(1024)
            text = text.decode()
            print(text)
            if text == "You have left the chat room. Goodbye!":
                time.sleep(2)
                break
    except socket.error as err:
        print("Lost connection with server.\nExiting...")
        time.sleep(2)
        quit()

def send_message():
    "Send message to server"
    try:
        while True:
            text = input()
            text = str.encode(text)
            if text != "":
                client.send(text)
            if (text.decode()).lower() == "exit":
                break
    except socket.error as err:
        print("Lost connection with server.\nExiting...")
        time.sleep(2)
        quit()

def quit():
    "Close the client's connection and exit the program"
    client.close()
    os._exit(0)

join_server()

"""
Active Threads:
- Main thread will handle sending messages to server
- A new thread (rt) is made for receiving message from server
"""
