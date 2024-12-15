import tarfile
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import messagebox

class Emulator:
    def __init__(self, config):
        self.username = config['username']
        self.hostname = config['hostname']
        self.vfs_path = config['vfs_path']
        self.log_path = config['log_path']
        self.current_directory = "/"
        self.load_vfs()

    def load_vfs(self):
        # Загрузка виртуальной файловой системы из tar
        with tarfile.open(self.vfs_path, 'r') as tar:
            tar.extractall(path="vfs")

    def log_action(self, action):
        # Логирование действий в XML формате
        try:
            root = ET.Element("log")
            action_element = ET.SubElement(root, "action")
            action_element.text = action
            tree = ET.ElementTree(root)
            tree.write(self.log_path)
        except Exception as e:
            print(f"Error logging action: {e}")

    def execute_command(self, command):
        if command == "ls":
            self.list_directory()
        elif command.startswith("cd "):
            self.change_directory(command[3:])
        elif command == "exit":
            self.exit_emulator()
        elif command == "whoami":
            self.show_username()
        elif command.startswith("rm "):
            self.remove_file(command[3:])
        else:
            messagebox.showerror("Error", "Unknown command")

    def list_directory(self):
        # Логика для команды ls
        messagebox.showinfo("Directory Listing", "Listing files...")  # Заглушка
        self.log_action("ls")

    def change_directory(self, path):
        # Логика для команды cd
        messagebox.showinfo("Change Directory", f"Changing directory to {path}...")  # Заглушка
        self.log_action(f"cd {path}")

    def exit_emulator(self):
        messagebox.showinfo("Exit", "Exiting emulator...")
        self.log_action("exit")

    def show_username(self):
        messagebox.showinfo("Who Am I", self.username)

    def remove_file(self, filename):
        # Логика для команды rm
        messagebox.showinfo("Remove File", f"Removing file {filename}...")  # Заглушка
        self.log_action(f"rm {filename}")

def load_config(file_path):
    import toml
    return toml.load(file_path)

def main():
    global root
    root = tk.Tk()
    root.title("Shell Emulator")

    config = load_config('config.toml')
    emulator = Emulator(config)

    def on_enter(event):
        command = entry.get()
        emulator.execute_command(command)
        entry.delete(0, tk.END)

    entry = tk.Entry(root)
    entry.bind("<Return>", on_enter)
    entry.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
