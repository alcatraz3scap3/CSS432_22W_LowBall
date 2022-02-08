import tkinter as tk
from tkinter import *
from tkinter import font
from random import randint
import time
import socket
from time import sleep
import threading

class Player():
    def __init__(self,name):
        self.name = name
        self.score = 0

class Game:
    player = Player('')

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Low Ball')
        self.welcome_screen()
        self.root.mainloop()

    def welcome_screen(self):
        self.welcome_frame = tk.Canvas(self.root, width=400, height=300, bg='#DCE0E1')
        self.welcome_frame.pack(fill=BOTH,expand=True)

        Label(self.welcome_frame, text='Enter name',
              bg='#DCE0E1', fg='#000000',
              font=('', 20)).pack(padx=10, pady=40)
        entry1 = tk.Entry(self.root)
        self.welcome_frame.create_window(200, 140, window=entry1)

        Button(self.welcome_frame, text='Submit', fg='#000000',
               command=lambda: self.connect_screen()).pack(padx=30, pady=30)
        self.player.name = entry1.get()

    def connect_screen(self):
        self.connect_frame = tk.Canvas(self.root, width=400, height=300, bg='#DCE0E1')
        self.connect_frame.pack(fill=BOTH, expand=True)
        label1 = tk.Label(self.connect_frame, text=self.player.name)
        self.connect_frame.create_window(200, 230, window=label1)


    # network client
client = None
HOST_ADDR = "0.0.0.0"
HOST_PORT = 8080

if __name__ == "__main__":
    Game()
