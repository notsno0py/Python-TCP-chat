import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from cryptography.fernet import Fernet

HOST = '127.0.0.1'
PORT = 5051
KEY = b'u7R6X_0_8WpP-vB-7v9X8zV_5_J3j_k_L_m_N_o_P_q='
cipher = Fernet(KEY)


class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
        except Exception as e:
            print(f"Unable to connect to server: {e}")
            return

        prompt_root = tkinter.Tk()
        prompt_root.withdraw()
        self.nickname = simpledialog.askstring("Nickname", "Please choose a name", parent=prompt_root)
        prompt_root.destroy()

        if not self.nickname:
            self.nickname = "Anonymous"

        self.running = True

        self.win = tkinter.Tk()
        self.win.title(f"Chat - {self.nickname}")
        self.win.configure(bg="#2c3e50")

        self.chat_label = tkinter.Label(self.win, text="Chat History:", bg="#2c3e50", fg="white")
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled', font=("Arial", 10), bg="#ecf0f1")

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="#2c3e50", fg="white")
        self.msg_label.config(font=("Arial", 12, "bold"))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3, font=("Arial", 10))
        self.input_area.pack(padx=20, pady=5)
        self.input_area.bind("<Return>", self.handle_enter)

        self.send_button = tkinter.Button(self.win, text="Send Message", command=self.write, bg="#27ae60", fg="white")
        self.send_button.config(font=("Arial", 11, "bold"))
        self.send_button.pack(padx=20, pady=10)

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        receive_thread = threading.Thread(target=self.receive, daemon=True)
        receive_thread.start()

        self.win.mainloop()

    def handle_enter(self, event):
        self.write()
        return "break"

    def write(self):
        message = self.input_area.get('1.0', 'end').strip()
        if message:
            full_message = f"{self.nickname}: {message}"
            encrypted_message = cipher.encrypt(full_message.encode('ascii'))
            self.sock.send(encrypted_message)
            self.input_area.delete('1.0', 'end')

    def receive(self):
        while self.running:
            try:
                raw_data = self.sock.recv(1024)
                if not raw_data:
                    break

                if raw_data == b'NICK':
                    self.sock.send(self.nickname.encode('ascii'))
                else:
                    decrypted_message = cipher.decrypt(raw_data).decode('ascii')

                    self.text_area.config(state='normal')
                    self.text_area.insert('end', decrypted_message + '\n')
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
            except Exception as e:
                print(f"Connection lost or error: {e}")
                break

    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass
        self.win.destroy()


if __name__ == "__main__":
    client = Client(HOST, PORT)