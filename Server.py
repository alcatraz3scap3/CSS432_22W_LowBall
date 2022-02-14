import tkinter as tk
import socket
import threading
from time import sleep

window = tk.Tk()
window.title("Server")

# create window
top_frame = tk.Frame(window)
btn_start = tk.Button(top_frame, text="Start", command=lambda: startServer())
btn_start.pack(side=tk.LEFT)
btn_stop = tk.Button(top_frame, text="Stop", command=lambda: stopServer(), state=tk.DISABLED)
btn_stop.pack(side=tk.LEFT)
top_frame.pack(side=tk.TOP, pady=(5, 0))

# columns for host and port information
middle_frame = tk.Frame(window)
addr_col = tk.Label(middle_frame, text="Address: X.X.X.X")
addr_col.pack(side=tk.LEFT)
port_col = tk.Label(middle_frame, text="Port:XXXX")
port_col.pack(side=tk.LEFT)
middle_frame.pack(side=tk.TOP, pady=(5, 0))

# display frame for client information
display_frame = tk.Frame(window)
title_line = tk.Label(display_frame, text="----------Client List----------").pack()
scroll_bar =tk.Scrollbar(display_frame)
scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
text_display = tk.Text(display_frame, height=10, width=30)
text_display.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scroll_bar.config(command=text_display.yview)
text_display.config(yscrollcommand=scroll_bar.set, background="green", highlightbackground="grey", state="disabled")
display_frame.pack(side=tk.BOTTOM, pady=(5, 10))

server = None
HOST_ADDR = "0.0.0.0"
HOST_PORT = 8080
player_name = " "
players = []
players_names = []
player_data = []
MAX_PLAYERS = 4

# start server
def startServer():
    global server, HOST_ADDR, HOST_PORT
    btn_start.config(state=tk.DISABLED)
    btn_stop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(10)

    threading.start_new_thread(acceptClients, (server, " "))

    addr_col["text"] = "Address: " + HOST_ADDR
    port_col["text"] = "Port: " + str(HOST_PORT)

# stop server
def stopServer():
    global server
    btn_stop.config(state=tk.DISABLED)
    btn_start.config(state=tk.NORMAL)

def acceptClients(a_server, y):
    while True:
        if len(players) < MAX_PLAYERS:
            new_player, addr = a_server.accept()
            players.append(new_player)
            # start new thread for every player
            threading.start_new_thread(ACKplayer(), (new_player, addr))

# ACK new player has joined the server
def ACKplayer(player_connection, player_ip):
    global server, player_name, players, player_data # WHY IS THIS HERE?????

    client_msg = " "
    player_name = player_connection.recv(4096)
    for x in range (1,MAX_PLAYERS+1):
        player_connection.send("Welcome Player " + x)

    players_names.append(player_name)
    updatePlayersDisplay(players_names)

    # or however we decide we want to start the game
    if len(players) == MAX_PLAYERS:
        sleep(1)
        # print player list to all players
        for plyr in players:
            for x in range(0, len(players)):
                plyr.send("opponent_name$" + players_names[x])



def updatePlayersDisplay(names):
    x = 1+1

window.mainloop()
