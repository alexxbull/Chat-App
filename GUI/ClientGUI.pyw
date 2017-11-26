import os
import time
import socket
import threading
import tkinter as tk
import tkinter.messagebox
import tkinter.scrolledtext as sct

client = socket.socket()                                                    # Client's socket object for, well, being a client
ui = tk.Tk()                                                                # variable for holding and performing GUI operations
rowCount = 0                                                                # variable to hold the current row - used in inital setup
name = ""                                                                   # variable to hold the username the client has entered, used in the inital setup
initialFrame = tk.Frame(ui)                                                 # variable to hold the inital setup GUI components in a frame
chatFrame = tk.Frame(ui, bg = "white")                                      # variable to hold the chat GUI components in a frame
chatText = sct.ScrolledText(chatFrame, wrap = tk.WORD, bd = 2)              # variable for printing text to the GUI window (chatFrame) with vertical scrollbars
ansEntry = tk.Entry(initialFrame, width = 30)                               # variable for the text box that the client enters their name in during the inital setup
sendTextBox = tk.Text(chatFrame, height = 5,  wrap = tk.WORD, bd = 2)       # variable to hold the client's text box for sending messages to the server

class ReceivingThread(threading.Thread):
    """A thread for listening for and receiving new messages from the server"""

    def run(self):
        receive_message()

class JoinServerThread(threading.Thread):
    """A thread for adding the client to the server (Needed for GUI to work properly)"""

    def run(self):
        join_server()

def join_server(h = "localhost", p = 8888):
    """Connect client to server"""
    global rowCount
    tk.Label(initialFrame, text = "Connecting to server...").grid(row = rowCount)
    rowCount+=1
    try:
        host = h
        post = p
        client.connect((host, post));
        tk.Label(initialFrame, text = "Connected!").grid(row = rowCount)
        rowCount+=1
    except socket.error as err:
        tk.Label(initialFrame, text = "Failed to connect to server.\n\nExiting...").grid(row = rowCount)
        rowCount+=1
        time.sleep(2)
        quit()
    else:
        send_username()

def send_username():
    """Complete username registration and then enter chat room"""
    global rowCount, initialFrame, name

    try:
        while True:
            getName = client.recv(1024)                                     # read server message for entering username
            getName = getName.decode()

            tk.Label(initialFrame, text = getName).grid(row = rowCount)
            ansEntry.grid(row = rowCount, column = 1)
            ansEntry.bind("<Return>", getusername_label)

            while (name == ""):                                             # will be updated when user clicks send button
                time.sleep(1)

            client.send(str.encode(name))                                   # send server the username entered
            valid = client.recv(1024)                                       # check if server approves of username
            valid = valid.decode()
            taken = "Username " + name + " is already taken."
            notTaken = name + " has entered the chat room."

            if valid == taken:
                tk.messagebox.showerror("Error", taken + "\nTry a different username.")
                name = ""
                continue
            elif valid == notTaken:
                initialFrame.destroy()
                make_chatGUI()
                printUI(notTaken)
                rt = ReceivingThread()
                rt.start()
                break
    except socket.error as err:
        tk.Label(initialFrame, text = "Lost connection with server.\n\nExiting...").grid(row = rowCount + 1)
        time.sleep(2)
        quit()

def receive_message():
    """Listen for messages from the server and display them."""
    try:
        while True:
            text = client.recv(1024)
            text = text.decode()
            printUI(text)
    except socket.error as err:
        printUI("Lost connection with server.\nExiting...")
        time.sleep(2)
        quit()

def send_message(event = None, textBox = sendTextBox):
    """Send messages to the server"""
    try:
        text = get_sendTextBox(event, textBox)
        text = str.encode(text)
        client.send(text)
        return "break"                                                      # prevents <Return> from inserting a new line so meaning cursor in text box returns the first line rather than second
    except socket.error as err:
        printUI("Lost connection with server.\nExiting...")
        time.sleep(2)
        quit()

def printUI(text):
    """Print text onto the GUI widget, chatText (equivalent to print() for the chatText widget)"""
    chatText.insert(tk.INSERT, text + "\n")
    chatText.see(tk.END)                                                    # focus on the last message printed (autoscroll)

def quit():
    """Close the client's connection and exit the program"""
    client.close()
    ui.destroy()
    os._exit(0)

def getusername_label(event):
    """Return the username the client entered during the inital setup process"""
    global name
    name = ansEntry.get()
    ansEntry.delete(0, tk.END)
    return name

def get_sendTextBox(event, textBox = sendTextBox):
    """Return the text the client entered in the sendTextBox widget (what the client wants to send to server)"""
    text = textBox.get("1.0", "end-1c")                                     # end-1c: end means read to end of text, but this adds newline. -1c mean remove 1 character
    textBox.delete("1.0", "end-1c")
    return text

def make_chatGUI():
    """Alter and make new GUI component after the client has entered the chat room"""
    # update main GUI window
    ui.title(name + " - Client.py")
    ui.minsize(width = 450, height = 200)
    ui.configure(bg = "white")
    ui.grid_rowconfigure(0, weight = 1)                                     # will allow GUI components in window to expand
    ui.grid_columnconfigure(0, weight = 1)                                  # will allow GUI components in window to expand

    chatFrame.grid_rowconfigure(0, weight = 1)                              # will allow GUI components in frame to expand
    chatFrame.grid_columnconfigure(0, weight = 1)                           # will allow GUI components in frame to expand
    chatFrame.grid(sticky = tk.N + tk.S + tk.E + tk.W)                      # will allow GUI components in frame to expand in all directions

    # make GUI component for the chat log
    chatText.grid(sticky = tk.N + tk.S + tk.E + tk.W)                       # expand in all directions if resized

    # make GUI component for the client to send messages
    sendTextBox.grid(row = 1, column = 0, sticky = tk.W)
    sendTextBox.bind("<Return>", send_message)
    sendTextBox.grid(sticky = tk.N + tk.S + tk.E + tk.W)                    # expand in all directions if resized

    # make a GUI button for the client to send messages in text box
    sendButton = tk.Button(chatFrame, text = "Send", width = 5, height = 1, command = send_message, bg = "white")
    sendButton.grid(row = 1, column = 1, sticky = tk.E)

def start_GUI():
    """Start the program with it's GUI elements"""
    ui.title("Client.py")
    ui.protocol("WM_DELETE_WINDOW", quit)
    initialFrame.grid()
    js = JoinServerThread()
    js.start()
    ui.mainloop()

start_GUI()
