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
HOST_ADDR = "192.168.1.34"
HOST_PORT = 8080

class Player():
    def __init__(self,name):
        self.name = name
        self.score = 0

class Game:
    player = Player('Test1')
    from_server = b""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Low Ball')
        self.root.geometry("1920x1080+10+20")
        self.welcome_screen()
        self.root.mainloop()

    def close_sck(self):
        self.client.close()

    def welcome_screen(self):
        self.welcome_frame = tk.Canvas(self.root, bg='#DCE0E1')
        self.welcome_frame.pack(fill=BOTH,expand=True)

        Label(self.welcome_frame, text='Enter name',
              bg='#DCE0E1', fg='#000000',
              font=('', 20)).pack(padx=10, pady=40)
        self.entry1 = tk.Entry(self.root)
        self.welcome_frame.create_window(200, 140, window=self.entry1)
        self.entry1.pack(side=tk.BOTTOM)

        Button(self.welcome_frame, text='Submit', fg='#000000',
               command=lambda: (self.set_player_name(), self.connect_screen())).pack()

    def set_player_name(self):
        self.player.name = self.entry1.get()

    def connect_screen(self):
        self.welcome_frame.pack_forget()
        self.entry1.destroy()
        self.connect_frame = tk.Canvas(self.root, bg='#DCE0E1')
        self.connect_frame.pack(fill=BOTH, expand=True)
        self.label1 = tk.Label(self.connect_frame, text=self.player.name, bg='#DCE0E1')
        self.label1.pack(side=tk.BOTTOM)
        self.connect_frame.create_window(950, 500, window=self.label1)

        Button(self.connect_frame, text='Connect', fg='#000000',
               command=lambda: (self.connect_to_server())).pack(padx=400, pady=200)

    def connect_to_server(self):
        #global client, HOST_PORT, HOST_ADDR
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((HOST_ADDR, HOST_PORT))
            self.client.send(self.player.name.encode())
            #client_thread = threading.Thread(target=self.receiveack, args=(self.client, "m"))
            #client_thread.start()
            self.receiveack(self.client, "m")
        except Exception as e:
            print(e)
            tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be unavailable. Try again later")

    def receiveack(self,sck,m):
        self.connect_frame.pack_forget()
        self.waiting_frame = tk.Canvas(self.root, bg='#DCE0E1')
        self.waiting_frame.pack(fill=BOTH, expand=True)
        self.wait_label = tk.Label(self.waiting_frame, text="Waiting on server...", bg='#DCE0E1')
        self.wait_label.pack(side=tk.BOTTOM)
        self.waiting_frame.create_window(950, 500, window=self.wait_label)
        self.root.after(0,self.wait_loop,sck)

        print("after loop")
        self.root.mainloop()

    def wait_loop(self,sck):
        while not self.from_server.decode().startswith("NAMES: "):
            print("in loop")
            self.from_server = sck.recv(4096)
            print("after recv")
            print(self.from_server.decode())


if __name__ == "__main__":
    Game()
