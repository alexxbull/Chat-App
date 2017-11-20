import socket
import threading
import sys

class ReceivingThread(threading.Thread):
    """A thread for listening for and receiving new messages from the server"""

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        try:
            receive_message()
        except socket.error as err:
            print("Lost connection with server.")
            sys.exit(1)
        else:
            end()


class SendingThread(threading.Thread):
    """A thread for sending messages from to the server"""

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        try:
            send_message()
        except socket.error as err:
            print("Lost connection with server.")
            sys.exit(1)
        else:
            end()

def create_client(h = "localhost", p = 8888):
    """Create a client socket"""
    global client
    try:
        client = socket.socket()
        host = h
        post = p
        client.connect((host, post));
    except socket.error as err:
        print("Failed to create client and connect to server.")
        sys.exit(1)
    else:
        send_username()

def send_username():
    global client, name, rt, st
    while True:
        getName = client.recv(1024)     # read server message for entering username
        getName = getName.decode()
        name = input(getName)

        client.send(str.encode(name))            # send server the username entered
        valid = client.recv(1024)       # check if server approves of name
        valid = valid.decode()
        taken = "Username " + name + " is already taken."
        if valid == taken:
            print(taken)
            continue
        else:
            rt = ReceivingThread()
            st = SendingThread(name)
            rt.start()
            st.start()
            break

def receive_message():
    """Listen for messages from the server and display them."""
    global client, name
    while True:
        text = client.recv(1024)
        text = text.decode()
        print(text)
        if text == "You have left the chat room. Goodbye!":
            break

def send_message():
    """Send message to server"""
    global client
    while True:
        # text = input("{0}: ".format(name))
        text = input()
        text = str.encode(text)
        client.send(text)
        if text.lower() == "exit":
            print("break response thread")
            break

def end():
    print(rt.isAlive())
    print(st.isAlive())
    if not st.isAlive() and not rt.isAlive():
        client.close()
        sys.exit(0)

def main():
    create_client()

main()
