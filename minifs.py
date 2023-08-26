import json
import base64
import os
import copy
class Exit(Exception):
    pass
class FileSys:
    current_drive = "c"  # Default drive
    drive_folder_path = os.path.join(os.path.expandvars("%LOCALAPPDATA%"), "minifs")
    VER = "Mini Filesystem [Bugfix 3 Features 3]"
    def __init__(self):
        self.current_path = []
        self.drive = {}
        self.load_drive(self.drive_folder_path + "\\" + self.current_drive)
    def cd(self, target_path=None):
        if target_path:
            target_folders = target_path.split("\\")
            current = self.drive
            for i in self.current_path:
                current = current[i]
            for i in target_folders:
                    if (i in current) and isinstance(current[i], dict):
                        current = current[i]
                        self.current_path.append(i)
                    elif i == "..":
                        self.current_path.pop()
                        current = self.drive
                        for i in self.current_path:
                            current = current[i]
                    else:
                        print("Target directory not found.")
                        return
        else:
            print(self.current_drive + "\\" + "\\".join(self.current_path))

    def dir(self, target_path=None):
        if not target_path:
            target_folders = ""
        else:
            target_folders = target_path.split("\\")
        current = self.drive
        current_path = copy.deepcopy(self.current_path)
        for i in self.current_path:
            current = current[i]
        for i in target_folders:
                if (i in current) and isinstance(current[i], dict):
                    current = current[i]
                    self.current_path.append(i)
                elif i == "..":
                    self.current_path.pop()
                    current = self.drive
                    for i in self.current_path:
                        current = current[i]
                else:
                    print("Target directory not found.")
                    self.current_path = current_path
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
        self.current_path = current_path
    def read(self, target):
        current = self.drive
        for folder in self.current_path:
            current = current[folder]
        if target in current and isinstance(current[target], str):
            print(current[target])
        else:
            print("Target is not a file.")
    def save_drive(self):
        path = os.path.join(drive_folder_path, f"{self.current_drive}")
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
        self.current_drive = drive_name
        self.save_drive()

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
        else:
            print("Invalid drive.")
    def write(self, filename):
        try:
            current = self.drive
            for folder in self.current_path:
                current = current[folder]
            a = base64.b16decode(input("Enter base-16 string: ").encode(), True)
            res = ""
            for i in a: res += chr(i)
            current[filename] = res
        except Exception as e:
            print("Error writing file: " + str(e))

    def write_(self, filename, a):
        current = self.drive
        for folder in self.current_path:
            current = current[folder]
        res = ""
        for i in a: res += chr(i)
        current[filename] = res
    
    def import_(self, path):
        if os.path.isfile(path):
            self.write_(os.path.basename(path), open(path, "rb").read())
        else:
            print("Invalid path / I don't support folder importing yet.")
    def export(self, file, dist):
        try:
            current = self.drive
            for folder in self.current_path:
                current = current[folder]
            if (file not in current) or (not isinstance(current[file], str)):
                print("Invalid path / I don't support folder exporting yet.")
            else:
                a = open(dist, "w")
                a.write(current[file])
                a.close()
        except Exception as e:
            print("Error exporting file: " + str(e))
    def run(self, code_) -> int:
        code_ = code_.splitlines() if "\n" in code_ else [code_]
        for i in code_:
            try:
                command = i.split(" ")
                if not command: pass
                elif command[0] == "dir":
                    if len(command) > 1:
                        self.dir(" ".join(command[1:]))
                    else:
                        self.dir()
                elif command[0] == "cd":
                    if len(command) > 1:
                        self.cd(" ".join(command[1:]))
                    else:
                        self.cd()
                elif command[0] == "read":
                    if len(command) > 1:
                        self.read(" ".join(command[1:]))
                elif command[0] == "mkdrv":
                    if len(command) > 1:
                        if not "\\" in " ".join(command[1:]):
                            self.new_drive(" ".join(command[1:]))
                        else:
                            print("Drive name mustn't contain backslashes")
                elif command[0] == "drv":
                    self.save_drive()
                    if len(command) > 1:
                        drive_file_path = os.path.join(drive_folder_path, f"{command[1].lower()}")
                        if os.path.exists(drive_file_path):
                            self.load_drive(drive_file_path)
                            self.current_drive = command[1]
                        else:
                            print("Drive not found.")
                elif command[0] == "mkdir":
                    if len(command) > 1:
                        if not "\\" in " ".join(command[1:]):
                            self.new_folder(" ".join(command[1:]))
                        else:
                            print("Path mustn't contain backslashes")
                elif command[0] == "del":
                    if len(command) > 1:
                        self.delete_item(" ".join(command[1:]))
                elif command[0] == "deldrv":
                    if len(command) > 1:
                        if command[1].lower() == "c":
                            print("Cannot delete the default 'c' drive.")
                        else:
                            self.delete_drive(command[1])
                elif command[0] == "write":
                    if len(command) > 1:
                        filename = " ".join(command[1:]).split("|", 1)[0]
                        if "\\" in filename:
                            print("Path mustn't contain backslashes.")
                        else:
                            data = " ".join(command[1:]).split("|", 1)[1]
                            self.write_(filename=filename, a=data)
                    if len(command) > 1:
                        if not "\\" in " ".join(command[1:]):
                            self.write(" ".join(command[1:]))
                        else:
                            print("Path mustn't contain backslashes")
                elif command[0] == "import":
                    if len(command) > 1:
                        self.import_(" ".join(command[1:]))
                elif command[0] == "export":
                    if len(command) > 1:
                        self.export(" ".join(command[1:]).split("|")[0], " ".join(command[1:]).split("|")[1])
                elif command[0] == "run":
                    if len(command) > 1:
                        return self.runfile(" ".join(command[1:]))
                elif command[0] == "exit":
                    self.save_drive()
                    raise Exit 
                elif command[0] == "cls":
                    os.system("cls")
                elif command[0] == "ver":
                    print(self.VER)
                elif command[0] == "help":
                    print("""Help:
Basic:
    help: help
    exit: exit
    cls: clear
    ver: show version
Create:
    mkdir <folder_name>: make folder
    mkdrv <drive_name>: make drive
    import <file_on_u_computer>: import that file, store it at current dir
Delete:
    del <file_or_folder>: delete file / folder
    deldrv <drive_name>: delete drive
View:
    dir: show current dir files / folders, support "\\" and ".."
    dir <folder>: show that dir files / folders, support "\\" and ".."
    cd: show current dir, support "\\" and ".."
    cd <folder>: go to that dir, support "\\" and ".."
    read <file>: show file contents
    drv <drive_name>: go to that drive
Other:
    export <file_in_this_prog>|<output_file_on_u_computer>: export to your computer ("|" included, example: "export a|c\\d")
    run <file>: run the file using this set of command""")
                else:
                    print("Unknown command: \"" + command[0] + "\"")
            except Exit as e:
                return 1
            except Exception as e:
                print("Error: " + str(e))
            self.save_drive()
        return 0
    def runfile(self, file):
        current = self.drive
        for i in self.current_path:
            current = current[i]
        if (file in current) and isinstance(current[file], str):
            return self.run(current[file])
        else:
            print("Invalid item.")
# Define the drive folder path (Windows-specific)
drive_folder_path = os.path.join(os.path.expandvars("%LOCALAPPDATA%"), "minifs")
os.makedirs(drive_folder_path, exist_ok=True)

# Example usage
self = FileSys()
print(f"{self.VER}\nType \"help\" to get help.")
while True:
    current_dir = os.path.abspath(os.path.join(drive_folder_path, *self.current_path))
    SEP = "\\"
    prompt = f"{self.current_drive}> " if not self.current_path else f"{self.current_drive}\\{SEP.join(self.current_path)}> "
    inp = input(prompt)
    if self.run(inp) == 1:
        break