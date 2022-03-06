import tkinter as tk
import socket
from threading import Thread
# from SocketServer import ThreadingMixIn
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
text_display.config(yscrollcommand=scroll_bar.set, background="#abffbc", highlightbackground="grey", state="disabled")
display_frame.pack(side=tk.BOTTOM, pady=(5, 10))

server = None
HOST_ADDR = "0.0.0.0"
HOST_PORT = 8080
players = []
out_players = []
MAX_PLAYERS = 1
MAX_SCORE = 100

class Player(Thread):
    score_array = []
    def __init__(self, name, socket, id):
        Thread.__init__(self)
        self.name = name
        self.playerSocket = socket
        self.id = id

    def addScore(self, points):
        # cumulative score array
        if len(self.score_array) != 0:
            points += self.score_array[0]
            self.score_array.append(points)
        else:
            self.score_array.append(points)
    def getScore(self):
        return self.score_array[len(self.score_array) - 1]
    def getName(self):
        return self.name
    def getID(self):
        id_str = str(self.id)
        return id_str

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

    acceptClients(server)

    addr_col["text"] = "Address: " + HOST_ADDR
    port_col["text"] = "Port: " + str(HOST_PORT)
# stop server
def stopServer():
    global server
    btn_stop.config(state=tk.DISABLED)
    btn_start.config(state=tk.NORMAL)

def acceptClients(a_server):
    player_number = 1
    while len(players) < MAX_PLAYERS:
        cliSock, address = a_server.accept()

        # ack client connection
        connected = "CONNECTED"
        cliSock.send(connected.encode())
        player_name = cliSock.recv(2048)
        new_player = Player(player_name.decode(), cliSock, player_number)
        print(new_player.name)
        players.append(new_player)
        new_player.start()

        player_number += 1
        updatePlayersDisplay()
    print("All Players Connected")  # DISPLAY THIS ON SCREEN

    sleep(3)
    # print player names to all players
    msg = "NAMES: "
    for x in range(0, len(players)):
        msg += players[x].name + " "
    for plyr in players:
        plyr.playerSocket.send(msg.encode())

    players[0].join()

    # let players all ACK the begining of the game
    players_ack = 0
    while not players_ack >= MAX_PLAYERS:
        for player in players:
            data = player.playerSocket.recv(4096).decode()
            if data.startswith("BEGIN"):
                players_ack += 1

    gamePlay()

def gamePlay():
    while True:
        for p in players:
            print(p.getName() + " player " + p.getID() + " turn")
            round_score = takeTurn(p)
            p.addScore(round_score)
            if p.getScore() >= MAX_SCORE:
                playerOut(p)
        print("ALL PLAYERS HAVE TAKEN THEIR TURN")
        sendScores()
        print("SENT SCORES TO PLAYERS")
        if len(players) < 2:
            endGame()

# ends the game and the program
def endGame():
    print("END GAME")
    winners = []
    # identify winner(s)
    # scenario 1: only 1 winner
    if len(players) == 1:
        winners.append(players[0])
    else:
        # scenario 2: multiple winners, players with the longest score arrays win
        longest_score_array = 0

        # find the longest score_array
        for player in out_players:
            if len(player.score_array) > longest_score_array:
                longest_score_array = len(player.score_array)

        # find players with that length score_array and add them to the winners list
        for player in out_players:
            if len(player.score_array) == longest_score_array:
                winners.append(player)

    # send winners to all players
    # make winners message in format "WINNERS: 1 2 3" or "WINNERS: 1"
    msg = "WINNERS: "
    for player in winners:
        msg += player.getID() + " "

    # send message
    for player in players:
        player.playerSocket.send(msg.encode())
    for player in out_players:
        player.playerSocket.send(msg.encode())

    # close sockets
    for player in players:
        player.playerSocket.close()
    for player in out_players:
        player.playerSocket.close()

    exit(2)

# sends every player all the players scores
def sendScores():
    # create the message
    msg = ""
    for player in players:
        msg += player.getID() + ": " + str(player.getScore()) + " "
    for player in out_players:
        msg += player.getID() + " YOUR OUT on round: " + len(player.score_array) + " "

    # send message
    for player in players:
        player.playerSocket.send(msg.encode())
    for player in out_players:
        player.playerSocket.send(msg.encode())

# removes and alerts player when they are at or over max points
def playerOut(player):
    # remove player from players list; add to out players
    players.remove(player)
    out_players.append(player)

    # tell player they are out of the game
    out = "OUT"
    player.playerSocket.send(out.encode())

def updatePlayersDisplay():
    print("here")
    text_display.config(state=tk.NORMAL)
    text_display.delete('1.0', tk.END)

    for c in players:
        if len(c.score_array) > 0:
            text_display.insert(tk.END, c.name + ': player ' + c.getID() + ' score: ' + c.getScore() + '\n')
        else:
            text_display.insert(tk.END, c.name + ': player ' + c.getID() + '\n')
    text_display.config(state=tk.DISABLED)

    if len(out_players) > 0:
        text_display.insert(tk.END, 'OUT PLAYERS: \n')
        for c in out_players:
            text_display.insert(tk.END, c.name + ' out on round: ' + len(c.score_array) + '\n')
    window.update()

# tells the player to take their turn, then tells player to wait for their next turn
def takeTurn(player):
    # p.playerSocket()
    print("TAKE TURN")
    play = "PLAY"
    wait = "WAIT"
    response = False
    score = 0

    # tell player to take their turn
    player.playerSocket.send(play.encode())
    print("player " + player.name + " turn, sent PLAY to client")

    # wait for player response
    while not response:
        data = player.playerSocket.recv(4096).decode()
        if data.startswith("SCORE: "):
            response = True
            score = int(data[7:])       # gets everything after SCORE:
            print(score)

    # tell player to wait for their next turn
    player.playerSocket.send(wait.encode())
    print("player " + player.name + " turn over, sent WAIT to client")
    return score

window.mainloop()
