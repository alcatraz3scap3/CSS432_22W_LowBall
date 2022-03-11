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
MAX_PLAYERS = 2
MAX_SCORE = 50
users = list()
already_saved = False

class User():   # for the user profile
    def __init__(self, username, games_won):
        self.username = username
        self.games_won = int(games_won)

class Player(Thread):   # for the game
    def __init__(self, name, socket, num):
        Thread.__init__(self)
        self.name = name
        self.playerSocket = socket
        self.num = num
        self.score_array = []
        self.stay_registered = True
        self.won = False

    def addScore(self, points):
        # cumulative score array
        if len(self.score_array) != 0:
            points += self.score_array[len(self.score_array) - 1]
            self.score_array.append(points)
        else:
            self.score_array.append(points)
    def getScore(self):
        return self.score_array[len(self.score_array) - 1]
    def getScoreS(self):
        score = self.getScore()
        score_s = "%s" % score
        return score_s
    def getName(self):
        return self.name
    def getNum(self):
        num_s = "%s" % self.num
        return num_s

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
        print("waiting for connections")
        cliSock, address = a_server.accept()

        # ack client connection; tell who is creating and who is joining the game
        connected = ""
        if player_number == 1:
            connected = "CONNECTED: CREATE"
        else:
            connected = "CONNECTED: JOIN"
        cliSock.send(connected.encode())

        # recv player data from client
        player_name = cliSock.recv(2048)
        new_player = Player(player_name.decode(), cliSock, player_number)
        print(new_player.name)
        players.append(new_player)
        new_player.start()

        player_number += 1
        updatePlayersDisplay()

    sleep(3)
    # print player names to all players
    msg = "NAMES: "
    for x in range(0, len(players)):
        msg += players[x].name + ": player " + players[x].getNum() + "\n"
    for plyr in players:
        plyr.playerSocket.send(msg.encode())

    # let players all ACK the beginning of the game
    players_ack = 0
    while not players_ack >= MAX_PLAYERS:
        for player in players:
            data = player.playerSocket.recv(4096).decode()
            if data.startswith("UNREG"):
                unregisterAndExit(player)
            if data.startswith("EXIT"):
                playerExit(player)
            if data.startswith("BEGIN"):
                players_ack += 1

    gamePlay()

def gamePlay():
    while True:
        for p in players:
            round_score = takeTurn(p)
            p.addScore(round_score)
            print("PLAYERS CUMULATIVE SCORE: ")
            print(p.getScoreS())
        all_checked = False
        while not all_checked:
            for p in players:
                if p.getScore() >= MAX_SCORE:
                    playerOut(p)
                    all_checked = False
                else:
                    all_checked = True
            if len(players) == 0:
                all_checked = True
        sendScores()
        updatePlayersDisplay()
        sleep(4)
        if len(players) < 2:
            endGame()

# ends the game and the program
def endGame():
    print("END GAME")
    winners = []
    # identify winner(s)

    # scenario 1: only 1 winner: all other players are out previous rounds
    if len(players) == 1:
        players[0].won = True
        winners.append(players[0])
    else:
        # scenario 2: multiple winners, players with the longest score arrays win (aka they hit max same round)
        longest_score_array = 0

        # find the longest score_array
        for player in out_players:
            if len(player.score_array) > longest_score_array:
                longest_score_array = len(player.score_array)

        # find players with that length score_array and add them to the winners list
        for player in out_players:
            if len(player.score_array) == longest_score_array:
                player.won = True
                winners.append(player)

    # send winners to all players
    # make winners message in format "WINNERS: 1 2 3" or "WINNERS: 1"
    msg = "WINNERS: "
    for player in winners:
        msg += player.getName() + ", player" + player.getNum() + "\n"

    # update server display
    text_display.config(state=tk.NORMAL)    # enables text_display editing
    text_display.delete('1.0', tk.END)  # deletes current text display

    text_display.insert(tk.END, msg)

    text_display.config(state=tk.DISABLED)  # disables text_display editing
    window.update()

    print(msg)
    sleep(4)
    # send message
    for player in players:
        player.playerSocket.send(msg.encode())
    for player in out_players:
        player.playerSocket.send(msg.encode())

    #check for unregstered users
    for player in players:
        data = player.playerSocket.recv(4096).decode()
        if data.startswith("UNREG"):
            unregisterAndExit(player)
        if data.startswith("EXIT"):
            playerExit(player)

    # close sockets
    for player in players:
        player.playerSocket.close()
    for player in out_players:
        player.playerSocket.close()

    global already_saved
    if not already_saved:
        savePlayers()

    # display global scoreboard
    text_display.config(state=tk.NORMAL)
    text_display.delete('1.0', tk.END)

    for c in users:
        print("HERE")
        text_display.insert(tk.END, c.username + ', games won: ' + str(c.games_won) + '\n')
    text_display.config(state=tk.DISABLED)
    window.update()
    sleep(5)
    exit(2)

# sends every player all the players scores
def sendScores():
    # create the message
    msg = "SCORES: "
    for player in players:
        msg += player.getName() + ", player " + player.getNum() + ": " + player.getScoreS() + "\n"
    for player in out_players:
        msg += player.getName() + ", player " + player.getNum() + " OUT round: " + str(len(player.score_array)) + " with score: " + player.getScoreS() + "\n"

    # send message
    for player in players:
        player.playerSocket.send(msg.encode())
    for player in out_players:
        player.playerSocket.send(msg.encode())

    # get ack from players that scores have been sent
    recvd = 0
    while recvd < MAX_PLAYERS:
        for player in players:
            print("waiting to recv ack from clis in PLAYERS")
            data = player.playerSocket.recv(4096).decode()
            if data.startswith("UNREG"):
                unregisterAndExit(player)
                recvd += 1
            if data.startswith("EXIT"):
                playerExit(player)
                recvd += 1
            if data.startswith("RECV SCORE"):
                recvd += 1
                print("GOT " + str(recvd) + " SCORE ACK in players from: " + player.getName())
                player.playerSocket.send("RECV ACK".encode())
            else:
                break
        for player in out_players:
            print("waiting to recv ack from clis FROM OUT PLAYERS")
            data = player.playerSocket.recv(4096).decode()
            if data.startswith("UNREG"):
                unregisterAndExit(player)
                recvd += 1
            if data.startswith("EXIT"):
                playerExit(player)
                recvd += 1
            if data.startswith("RECV SCORE"):
                recvd += 1
                print("GOT " + str(recvd) + " SCORE ACK in players_out from: " + player.getName())
                player.playerSocket.send("RECV ACK".encode())
            else:
                break


# removes and alerts player when they are at or over max points
def playerOut(player):
    print("REMOVING PLAYER: " + player.getName() + ", player " + player.getNum())

    # remove player from players list; add to out players
    players.remove(player)
    out_players.append(player)

    # tell player they are out of the game: include for more than
    # out = "OUT"
    # player.playerSocket.send(out.encode())

def updatePlayersDisplay():
    text_display.config(state=tk.NORMAL)
    text_display.delete('1.0', tk.END)

    for c in players:
        if len(c.score_array) > 0:
            text_display.insert(tk.END, c.getName() + ', player ' + c.getNum() + ' score: ' + c.getScoreS() + '\n')
        else:
            text_display.insert(tk.END, c.getName() + ', player ' + c.getNum() + '\n')

    if len(out_players) > 0:
        text_display.insert(tk.END, 'OUT PLAYERS: \n')
        for c in out_players:
            text_display.insert(tk.END, c.getName() + ' out on round: ' + str(len(c.score_array)) + '\n')

    text_display.config(state=tk.DISABLED)
    window.update()

# tells the player to take their turn, then tells player to wait for their next turn
def takeTurn(player):
    play = "PLAY"
    wait = "WAIT"
    response = False
    score = 0

    # tell player to take their turn
    player.playerSocket.send(play.encode())

    # wait for player response
    while not response:
        data = player.playerSocket.recv(4096).decode()
        if data.startswith("UNREG"):
            unregisterAndExit(player)
            response = True
        if data.startswith("EXIT"):
            playerExit(player)
            response = True
        if data.startswith("SCORE: "):
            response = True
            score = int(data[7:])       # gets everything after SCORE:
            print("PLAYER SENT SCORE: ")
            print(score)

    # tell player to wait for their next turn
    player.playerSocket.send(wait.encode())
    print("player " + player.getName() + " turn over, sent WAIT to client")
    return score

def savePlayers():
    f = open("users.txt", "r")  # "r" says we are reading from the file
    # loop through the file and put all the username - game won pairs into a list
    for user in f:
        space = user.find(' ')  # everything before space is the name, after is the # of times the user has won a game
        username = user[0:space]  # gets the username (aka everything before the space)
        games_won = user[(space + 1):]  # gets the # of games won (aka everything after the space)
        new_user = User(username, games_won)
        users.append(new_user)

    #   update the list of players who wish to stay registered
    for player in players:
        if player.stay_registered:
            if player.won:
                registerUser(player.getName(), 1)   # add 1 to the games_won
            else:
                registerUser(player.getName(), 0)   # add 0 to the games_won
        else:
            removeUser(player.getName())

    for player in out_players:
        if player.stay_registered:
            if player.won:
                registerUser(player.getName(), 1)   # add 1 to the games_won
            else:
                registerUser(player.getName(), 0)   # add 0 to the games_won
        else:
            removeUser(player.getName())
    f.close()

    #   re-write all users to the user file
    f = open("users.txt", "w")
    for user in users:
        f.write(user.username + " " + str(user.games_won) + "\n")
    f.close()


def removeUser(name):
    for user in users:
        if user.username == name:
            users.remove(user)

# register new users and update existing users
def registerUser(name, won):
    in_list = False
    index = 0

    # find the user & index
    for user in users:
        if user.username == name:
            in_list = True
            break
        index += 1

    if not in_list:
        new_user = User(name, won)
        users.append(new_user)
    else:
        users[index].games_won += won

def unregisterAndExit(player):
    player.stay_registered = False

    players.remove(player)

    in_list = False
    for p in out_players:
        if p.getName() == player.getName():
            in_list = True

    if not in_list:
        out_players.append(player)

    player.playerSocket.send('EXIT'.encode())

    if len(players) > 0:
        players[0].won = True

    for p in out_players:
        if p.getName() != player.getName():
            p.won = True

    global already_saved
    if not already_saved:
        savePlayers()
        already_saved = True

    out_players.remove(player)
    endGame()

def playerExit(player):
    players.remove(player)

    in_list = False
    for p in out_players:
        if p.getName() == player.getName():
            in_list = True

    if not in_list:
        out_players.append(player)
    player.playerSocket.send('EXIT'.encode())

    if len(players) > 0:
        players[0].won = True

    for p in out_players:
        if p.getName() != player.getName():
            p.won = True

    global already_saved
    if not already_saved:
        savePlayers()
        already_saved = True

    out_players.remove(player)
    endGame()

window.mainloop()
