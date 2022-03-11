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
HOST_ADDR = "10.156.3.172"
HOST_PORT = 8080



class Player():
    def __init__(self, name):
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
        self.welcome_frame.pack(fill=BOTH, expand=True)

        Label(self.welcome_frame, text='Enter name',
              bg='#DCE0E1', fg='#000000',
              font=('', 20)).pack(padx=10, pady=40)
        self.entry1 = tk.Entry(self.root)
        self.welcome_frame.create_window(200, 140, window=self.entry1)
        self.entry1.pack(side=tk.BOTTOM)

        Button(self.welcome_frame, text='Submit', fg='#000000',
               command=lambda: (self.set_player_name(), self.connect_screen())).pack()
        self.test_display = tk.Text(self.root, height=30, width=90)
        self.test_display.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        self.test_display.config(background="#abffbc", highlightbackground="grey", state="disabled")

    def set_player_name(self):
        self.player.name = self.entry1.get()

    def connect_screen(self):
        self.file = open("server_ip.txt", "a")  #to create the file
        self.file.close()
        self.file = open("server_ip.txt", "r")
        self.welcome_frame.pack_forget()
        self.entry1.destroy()
        self.connect_frame = tk.Canvas(self.root, bg='#DCE0E1')
        self.connect_frame.pack(fill=BOTH, expand=True)
        # self.label1 = tk.Label(self.connect_frame, text=self.player.name, bg='#DCE0E1')
        # self.label1.pack(side=tk.BOTTOM)
        self.test_display.config(state=tk.NORMAL)
        #print(self.file.read())
        self.file_content = self.file.read().rstrip()
        print(self.file_content)
        self.file.close()
        m = 'Please enter IP address of server to continue \n' + 'Last used IP address: ' + self.file_content + '\n' + self.player.name + ': ' + str(self.player.score) + '\n'
        self.test_display.insert(tk.END, m)
        self.test_display.config(state=tk.DISABLED)
        # self.connect_frame.create_window(950, 500, window=self.label1)
        self.entry2 = tk.Entry(self.connect_frame)
        self.connect_frame.create_window(200, 140, window=self.entry2)
        self.entry2.pack(side=tk.BOTTOM)

        Button(self.connect_frame, text='Connect', fg='#000000',
               command=lambda: (self.connect_to_server())).pack(padx=400, pady=200)

    def connect_to_server(self):
        # global client, HOST_PORT, HOST_ADDR
        try:
            self.file = open("server_ip.txt", "w")
            self.file.write(self.entry2.get())
            self.file.close()
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.entry2.get(), HOST_PORT))
            self.client.send(self.player.name.encode())
            # client_thread = threading.Thread(target=self.receiveack, args=(self.client, "m"))
            # client_thread.start()
            self.receiveack(self.client, "m")
        except Exception as e:
            print(e)
            tk.messagebox.showerror(title="ERROR!!!",
                                    message="Cannot connect to host: " + self.file_content + " on port: " + str(
                                        HOST_PORT) + " Server may be unavailable. Try again later")

    def receiveack(self, sck, m):
        self.connect_frame.pack_forget()
        self.waiting_frame = tk.Canvas(self.root, bg='#DCE0E1')
        self.waiting_frame.pack(fill=BOTH, expand=True)
        self.wait_label = tk.Label(self.waiting_frame, text="Waiting on server...", bg='#DCE0E1')
        self.wait_label.pack(side=tk.BOTTOM)
        self.waiting_frame.create_window(950, 500, window=self.wait_label)
        self.root.after(500, self.wait_loop, sck)

    def wait_loop(self, sck):
        while not self.from_server.decode().startswith("NAMES: "):
            self.from_server = sck.recv(4096)
            print(self.from_server.decode())
            print(self.from_server.decode().startswith("NAMES: "))
        sck.send("BEGIN".encode())
        self.root.after(0, self.initialize_names, sck)

    def initialize_names(self, sck):
        print("in init names")
        self.test_display.config(state=tk.NORMAL)
        self.test_display.delete("1.0", "end")
        message = ""
        message += self.from_server.decode()[7:]
        print(message)
        self.test_display.insert(tk.END, message + '\n')
        self.test_display.config(state=tk.DISABLED)
        self.root.update()
        self.root.after(0, self.after_loop(sck))

    def after_loop(self, sck):
        Button(self.waiting_frame, text='Continue', fg='#000000', command=lambda: (self.main_screen(sck))).pack()
        self.root.mainloop()

    def main_screen(self, sck):
        dice_list = [1, 2, 0, 4, 5, 6]
        self.dice_values = [1, 2, 0, 4, 5, 6]
        self.dice_selected = False
        self.rerolls = 0
        self.turn = 1

        self.dice_values[0] = random.choice(dice_list)
        self.dice_values[1] = random.choice(dice_list)
        self.dice_values[2] = random.choice(dice_list)
        self.dice_values[3] = random.choice(dice_list)
        self.dice_values[4] = random.choice(dice_list)
        self.dice_values[5] = random.choice(dice_list)

        self.all_disabled = False
        print("in main screen")
        self.waiting_frame.pack_forget()
        self.main_frame = tk.Canvas(self.root, bg='#DCE0E1')
        self.main_frame.pack(fill=BOTH, expand=True)
        self.d1 = Button(self.main_frame, text=self.dice_values[0], font=('', 15), width=6, height=3,
                         command=lambda: self.on_click(0, sck))
        self.d2 = Button(self.main_frame, text=self.dice_values[1], font=('', 15), width=6, height=3,
                         command=lambda: self.on_click(1, sck))
        self.d3 = Button(self.main_frame, text=self.dice_values[2], font=('', 15), width=6, height=3,
                         command=lambda: self.on_click(2, sck))
        self.d4 = Button(self.main_frame, text=self.dice_values[3], font=('', 15), width=6, height=3,
                         command=lambda: self.on_click(3, sck))
        self.d5 = Button(self.main_frame, text=self.dice_values[4], font=('', 15), width=6, height=3,
                         command=lambda: self.on_click(4, sck))
        self.d6 = Button(self.main_frame, text=self.dice_values[5], font=('', 15), width=6, height=3,
                         command=lambda: self.on_click(5, sck))

        self.reroll_btn = Button(self.main_frame, text='Reroll', fg='#000000', command=lambda: (self.reroll()))
        self.exit_btn = Button(self.main_frame, text="Exit", fg='#000000', command=lambda: (self.exit_game(sck)))
        self.unreg_btn = Button(self.main_frame, text="Exit & \nunregister", fg='#000000',
                                command=lambda: (self.unreg_game(sck)))
        # self.reroll.pack(padx=400, pady=200, side=tk.BOTTOM)

        self.d1.grid(row=0, column=0)
        self.d2.grid(row=0, column=1)
        self.d3.grid(row=0, column=2)
        self.d4.grid(row=1, column=0)
        self.d5.grid(row=1, column=1)
        self.d6.grid(row=1, column=2)
        self.reroll_btn.grid(row=2, column=2)
        self.exit_btn.grid(row=2, column=1)
        self.unreg_btn.grid(row=2, column=0)

        # self.player_scores = tk.Canvas(self.root, bg='#DCE0E1')
        # self.player_scores.pack(fill=BOTH, expand=True, side=tk.RIGHT)

        self.dice_btn_list = [self.d1, self.d2, self.d3, self.d4, self.d5, self.d6]
        self.wait_play(sck)
        self.root.update()

    def wait_play(self, sck):
        print("in wait_play")
        self.from_server = b""
        for child in self.main_frame.winfo_children():
            child.configure(state='disable')
        while not self.from_server.decode().startswith("PLAY"):
            self.from_server = sck.recv(4096)
            print(self.from_server.decode())
            print(self.from_server.decode().startswith("PLAY"))
            self.d1.grid(row=0, column=0)
            self.d2.grid(row=0, column=1)
            self.d3.grid(row=0, column=2)
            self.d4.grid(row=1, column=0)
            self.d5.grid(row=1, column=1)
            self.d6.grid(row=1, column=2)
            self.reroll_btn.grid(row=100, column=150)
            if self.from_server.decode().startswith("SCORES: "):
                self.the_message = self.from_server.decode()
                while not self.from_server.decode().startswith("RECV ACK"):
                    sck.send(("RECV SCORE " + self.player.name).encode())
                    self.from_server = sck.recv(4096)
                self.get_scores()
                self.from_server = b""
            if self.from_server.decode().startswith("WINNERS:"):
                break

        if self.from_server.decode().startswith("WINNERS:"):
            self.end_game(sck)
            self.root.update()
        for child in self.main_frame.winfo_children():
            child.configure(state='normal')
        self.root.mainloop()

    def end_game(self, sck):
        self.main_frame.pack_forget()
        self.end_screen = tk.Canvas(self.root, bg='#DCE0E1')
        self.end_screen.pack(fill=BOTH, expand=True)
        Button(self.end_screen, text='Exit', fg='#000000',
               command=lambda: (self.exit_game(sck))).pack(padx=400, pady=200)
        message = ""
        message += self.from_server.decode()[9:]
        tk.messagebox.showerror(title="Game Over!", message="Winners are: " + message)
        self.root.mainloop()

    def get_scores(self):
        self.test_display.config(state=tk.NORMAL)
        self.test_display.delete("1.0", "end")
        message = ""
        message += self.the_message[7:]
        print(message)
        self.test_display.insert(tk.END, message + '\n')
        self.test_display.config(state=tk.DISABLED)
        self.root.update()

    def reroll(self):
        dice_list = [1, 2, 0, 4, 5, 6]
        print("rerolls: " + str(self.rerolls))
        print("dice_selected: " + str(self.dice_selected))
        if self.dice_selected:
            i = 0
            for btn in self.dice_btn_list:
                if btn["state"] == "normal":
                    self.dice_values[i] = random.choice(dice_list)
                    btn["text"] = self.dice_values[i]
                i += 1
            self.rerolls += 1
            self.dice_selected = False
        else:
            tk.messagebox.showerror(title="Input needed!", message="Cannot reroll dice until one has been selected!")

    def check_if_selected(self):
        selected = False
        for btn in self.dice_btn_list:
            if btn["state"] == "disabled":
                selected = True
        return selected

    def on_click(self, index, sck):
        self.dice_btn_list[index]["state"] = "disabled"
        self.dice_selected = True
        print("current player score: " + str(self.player.score))
        print("dice value: " + str(self.dice_values[index]))
        self.player.score += self.dice_values[index]
        self.check_btns(sck)
        print("Score: " + str(self.player.score))
        print("dice_selected: " + str(self.dice_selected))

    def check_btns(self, sck):
        self.all_disabled = True
        for btn in self.dice_btn_list:
            if btn["state"] == "normal":
                self.all_disabled = False
        if self.all_disabled:
            print("all buttons are disabled")
            sck.send(("SCORE: " + str(self.player.score)).encode())
            self.turn += 1
            self.after_turn(sck)

    def after_turn(self, sck):
        self.player.score = 0
        dice_list = [1, 2, 0, 4, 5, 6]
        i = 0
        for btn in self.dice_btn_list:
            btn["state"] = "disabled"
            self.dice_values[i] = random.choice(dice_list)
            btn["text"] = self.dice_values[i]
            i += 1
        self.wait_play(sck)

    def exit_game(self, sck):
        sck.send("EXIT".encode())
        # wait for server to get exit?
        self.from_server = b""
        while not self.from_server.decode().startswith("EXIT"):
            self.from_server = sck.recv(4096)
        self.close_sck()
        self.root.destroy()
        exit(0)

    def unreg_game(self, sck):
        sck.send("UNREG".encode())
        # wait for server to get exit?
        while not self.from_server.decode().startswith("EXIT"):
            self.from_server = sck.recv(4096)
        self.close_sck()
        self.root.destroy()


if __name__ == "__main__":
    Game()
