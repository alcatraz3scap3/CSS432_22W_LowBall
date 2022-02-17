import tkinter as tk
from tkinter import messagebox
from tkinter import *
from tkinter import font
from random import randint
import time
import socket
from time import sleep
import threading
import socket

client = None
HOST_ADDR = "10.156.28.126"
HOST_PORT = 8080

class Player():
    def __init__(self,name):
        self.name = name
        self.score = 0

class Game:
    player = Player('Test1')

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
        self.entry1 = tk.Entry(self.root)
        self.welcome_frame.create_window(200, 140, window=self.entry1)
        self.entry1.pack(side=tk.BOTTOM)

        Button(self.welcome_frame, text='Submit', fg='#000000',
               command=lambda: (self.set_player_name(), self.connect_screen())).pack(padx=30, pady=30)

    def set_player_name(self):
        self.player.name = self.entry1.get()

    def connect_screen(self):
        self.welcome_frame.pack_forget()
        self.entry1.destroy()
        self.connect_frame = tk.Canvas(self.root, width=400, height=300, bg='#DCE0E1')
        self.connect_frame.pack(fill=BOTH, expand=True)
        self.label1 = tk.Label(self.connect_frame, text=self.player.name, bg='#DCE0E1')
        self.label1.pack(side=tk.TOP)
        self.connect_frame.create_window(200, 230, window=self.label1)

        Button(self.connect_frame, text='Connect', fg='#000000',
               command=lambda: (self.connect_to_server()())).pack(padx=30, pady=30)

    def connect_to_server(self):
        global client, HOST_PORT, HOST_ADDR
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST_ADDR, HOST_PORT))
            client.send(self.player.name)
            threading.start_new_thread(receive_ACK(), (client, "m"))
        except Exception as e:
            tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be unavailable. Try again later")

    def receive_ACK(self,sck,m):
        from_server = sck.recv(4096)
        print(from_server)

if __name__ == "__main__":
    Game()
