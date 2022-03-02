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
import random

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
        self.root.after(500,self.wait_loop,sck)

    def wait_loop(self,sck):
        while not self.from_server.decode().startswith("NAMES: "):
            print("in loop")
            self.from_server = sck.recv(4096)
            print("after recv")
            print(self.from_server.decode())
            print(self.from_server.decode().startswith("NAMES: "))
        self.root.after(0, self.after_loop, sck)

    def after_loop(self, sck):
        Button(self.waiting_frame, text='Continue', fg='#000000', command=lambda: (self.main_screen(sck))).pack()
        print("after loop")
        self.root.mainloop()

    def main_screen(self,sck):
        dice_list = [1, 2, 3, 4, 5, 6]
        self.all_disabled = False
        print("in main screen")
        self.waiting_frame.pack_forget()
        self.main_frame = tk.Canvas(self.root, bg='#DCE0E1')
        self.main_frame.pack(fill=BOTH, expand=True)
        self.d1 = Button(self.main_frame,text=random.choice(dice_list),font=('',15), width=6, height=3, command=lambda: self.on_click(0))
        self.d2 = Button(self.main_frame, text=random.choice(dice_list), font=('', 15), width=6, height=3, command=lambda: self.on_click(1))
        self.d3 = Button(self.main_frame, text=random.choice(dice_list), font=('', 15), width=6, height=3, command=lambda: self.on_click(2))
        self.d4 = Button(self.main_frame, text=random.choice(dice_list), font=('', 15), width=6, height=3, command=lambda: self.on_click(3))
        self.d5 = Button(self.main_frame, text=random.choice(dice_list), font=('', 15), width=6, height=3, command=lambda: self.on_click(4))
        self.d6 = Button(self.main_frame, text=random.choice(dice_list), font=('', 15), width=6, height=3, command=lambda: self.on_click(5))

        self.reroll_btn = Button(self.main_frame, text='Reroll', fg='#000000', command=lambda: (self.reroll()))\
        #self.reroll.pack(padx=400, pady=200, side=tk.BOTTOM)

        self.d1.grid(row=0, column=0)
        self.d2.grid(row=0, column=1)
        self.d3.grid(row=0, column=2)
        self.d4.grid(row=1, column=0)
        self.d5.grid(row=1, column=1)
        self.d6.grid(row=1, column=2)
        self.reroll_btn.grid(row=100, column=150)

        self.dice_btn_list = [self.d1, self.d2, self.d3, self.d4, self.d5, self.d6]



    def reroll(self):
        dice_list = [1, 2, 3, 4, 5, 6]
        for btn in self.dice_btn_list:
            if btn["state"] == "normal":
                btn["text"] = random.choice(dice_list)


    def on_click(self, index):
        self.dice_btn_list[index]["state"] = "disabled"
        self.check_btns()

    def check_btns(self):
        self.all_disabled = True
        for btn in self.dice_btn_list:
            if btn["state"] == "normal":
                print("here")
                self.all_disabled = False
        if self.all_disabled:
            print("all buttons are disabled")

if __name__ == "__main__":
    Game()
