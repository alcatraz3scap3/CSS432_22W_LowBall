import tkinter as tk
import socket
import threading
from time import sleep

MAX_SCORE = 100
players = []

class Player:
    def __init__(self, name, score):
        self.name = name
        self.score = 0

def game_logic():
    # add the players to a list
    still_playing = True

    while(still_playing):
        still_playing = False
        # start game loop

        # allow each player to take their turn

        # add each player's score to their score

        # check if any player is at or over 100

        # if more than 1 player is still in, loop back

        # if 1 player is still in, that player wins

        # if no players are in, no one wins
