import json
import base64
import os

class DictFileSystem:
    current_drive = "c"  # Default drive
    drive_folder_path = os.path.join(os.path.expandvars("%LOCALAPPDATA%"), "minifs")
    def __init__(self):
        self.current_path = []
        self.drive = {}
        self.load_drive(self.drive_folder_path + "\\" + self.current_drive)

    def cd(self, target_path=None):
        if target_path:
            target_folders = target_path.split("\\")
            for folder in target_folders:
                if folder == "..":
                    if self.current_path:
                        self.current_path.pop()
                else:
                    current = self.drive
                    for folder in self.current_path:
                        current = current[folder]
                    if folder in current and isinstance(current[folder], dict):
                        self.current_path.append(folder)
                    else:
                        print("Target directory not found: " + folder)
        else:
            print(self.current_drive + "\\" + "\\".join(self.current_path))

    def dir(self, target_path=None):
        if not target_path:
            target_path = self.current_path
            target_folders = target_path
        else:
            target_folders = target_path.split("\\")
        current = self.drive
        for folder in target_folders:
            if folder in current and isinstance(current[folder], dict):
                current = current[folder]
            else:
                print("Target directory not found.")
                return
        folders, files = [], []
        for item in current.keys():
            if isinstance(current[item], dict):
                folders.append(item)
            elif isinstance(current[item], str):
                files.append(item)
        for file in files:
            print(f"file {file}")
        for folder in folders:
            print(f"folder {folder}")

    def truncate_file(self, target):
        current = self.drive
        for folder in self.current_path:
            current = current[folder]
        if target in current and isinstance(current[target], str):
            current[target] = ""

    def echo(self, target):
        current = self.drive
        for folder in self.current_path:
            current = current[folder]
        if target in current and isinstance(current[target], str):
            print(current[target])
        else:
            print("Target is not a file.")

    def save_drive(self):
        path = os.path.join(drive_folder_path, f"{self.current_drive.lower()}")
        drive_json = json.dumps(self.drive, indent=4)
        drive_b64 = base64.b64encode(drive_json.encode("utf-8"))
        with open(path, "wb") as f:
            f.write(drive_b64)

    def load_drive(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                drive_b64 = f.read()
                try:
                    drive_json = base64.b64decode(drive_b64).decode("utf-8")
                    self.drive = json.loads(drive_json)
                except Exception as e:
                    print("Error loading drive:", e)
                    self.drive = {}
        else:
            print("Drive file not found, starting with empty drive.")

    def new_drive(self, drive_name):
        self.save_drive()  # Save the current drive before creating a new one
        self.drive = {}
        self.current_path = []
        global current_drive
        current_drive = drive_name
        drive_file_path = os.path.join(drive_folder_path, f"{drive_name.lower()}")
        self.save_drive(drive_file_path)

    def new_file(self, file_name):
        current = self.drive
        for folder in self.current_path:
            current = current[folder]
        current[file_name] = ""

    def new_folder(self, folder_name):
        current = self.drive
        for folder in self.current_path:
            current = current[folder]
        current[folder_name] = {}

    def delete_item(self, item_name):
        current = self.drive
        for folder in self.current_path:
            current = current[folder]
        if item_name in current:
            del current[item_name]
        else:
            print("Item not found.")

    def delete_drive(self, drive_name):
        drive_file_path = os.path.join(drive_folder_path, f"{drive_name.lower()}")
        if os.path.exists(drive_file_path):
            os.remove(drive_file_path)
            if self.current_drive == drive_name:
                self.current_drive = "c"

# Define the drive folder path (Windows-specific)
drive_folder_path = os.path.join(os.path.expandvars("%LOCALAPPDATA%"), "minifs")
os.makedirs(drive_folder_path, exist_ok=True)

# Example usage
file_system = DictFileSystem()

while True:
    current_dir = os.path.abspath(os.path.join(drive_folder_path, *file_system.current_path))
    SEP = "\\"
    prompt = f"{file_system.current_drive}> " if not file_system.current_path else f"{file_system.current_drive}\\{SEP.join(file_system.current_path)}> "
    command = input(prompt).split()
    if not command:
        continue
    elif command[0] == "dir":
        if len(command) > 1:
            file_system.dir(command[1])
        else:
            file_system.dir()
    elif command[0] == "cd":
        if len(command) > 1:
            file_system.cd(command[1])
        else:
            file_system.cd()
    elif command[0] == "echo":
        if len(command) > 1:
            file_system.echo(command[1])
    elif command[0] == "save":
        file_system.save_drive()
    elif command[0] == "exit":
        file_system.save_drive()
        break
    elif command[0] == "newd":
        if len(command) > 1:
            file_system.new_drive(command[1])
    elif command[0] == "cdd":
        file_system.save_drive()
        if len(command) > 1:
            drive_file_path = os.path.join(drive_folder_path, f"{command[1].lower()}")
            if os.path.exists(drive_file_path):
                file_system.load_drive(drive_file_path)
                file_system.current_drive = command[1]
            else:
                print("Drive not found.")
    elif command[0] == "newf":
        if len(command) > 1:
            file_system.new_file(command[1])
    elif command[0] == "newfo":
        if len(command) > 1:
            file_system.new_folder(command[1])
    elif command[0] == "del":
        if len(command) > 1:
            file_system.delete_item(command[1])
    elif command[0] == "deld":
        if len(command) > 1:
            if command[1].lower() == "c":
                print("Cannot delete the default 'c' drive.")
            else:
                file_system.delete_drive(command[1])
    elif command[0] == "help":
        print("Available commands: dir, cd, echo, save, exit, newd, cdd, newf, newfo, del, deld, help")
    else:
        print("Unknown command.")
    file_system.save_drive()