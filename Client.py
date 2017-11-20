import socket
import threading

client = socket.socket()

class ReceivingThread(threading.Thread):
    """A thread for listening for and receiving new messages from the server"""

    def run(self):
        """Listen for messages from the server and display them."""
        try:
            receive_message()
        except socket.error as err:
            print("Lost connection with server.")

class SendingThread(threading.Thread):
    """A thread for sending messages from to the server"""

    def __init__(self, name):
        threading.Thread.__init__(self, name = name)

    def run(self):
        """Listen for messages from the server and display them."""
        try:
            send_message()
        except socket.error as err:
            print("Lost connection with server.")

def join_server(h = "localhost", p = 8888):
    """Connect client to server"""
    global client
    try:
        host = h
        post = p
        client.connect((host, post));
    except socket.error as err:
        print("Failed to connect to server.")
    else:
        send_username()

def send_username():
    global client
    try:
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
    except socket.error as err:
        print("Lost connection with server.")

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
        text = input()
        text = str.encode(text)
        client.send(text)
        if (text.decode()).lower() == "exit":
            break
def main():
    join_server()

main()
