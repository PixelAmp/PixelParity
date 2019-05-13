import os, paramiko, sys, time, select, re
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

from tkinter import *
from shutil import copyfile
'''
Check if path is a file or just the directory
    If it is the directly ask if you want to send all files from drive to the path
In a future update allow the ability to copy files locally

'''
class ToolBox(object):
    channel = paramiko.SSHClient()
    ip= 'PixelZero.local' #'192.168.0.19' #'PixelDac.local'
    user='pi'
    password='0000'

def initSSH(ip=ToolBox.ip, user=ToolBox.user, password=ToolBox.password):
    channel = paramiko.SSHClient()
    channel.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        channel.connect(ip, username=user, password=password, port=22, timeout=2)
        #ToolBox.channel = channel
        ToolBox.sftp = channel.open_sftp()
        #print('Successful ssh and sftp\n')
        return True
    except Exception as Error:
        messagebox.showerror(message=Error)
        return False

#does an ftp of the local path to the remote path
def SendIt(LocalPath,RemotePath):
    initSSH()
    print(LocalPath)
    print(RemotePath)
    try:
        ToolBox.sftp.put(LocalPath, RemotePath)
    except Exception as Error:
        messagebox.showerror(message=Error)
        return False
        

#does an ftp of the remote path to the local path
def GetIt(LocalPath,RemotePath):
    initSSH()
    print(LocalPath)
    print(RemotePath)
    try:
        ToolBox.sftp.get(RemotePath,LocalPath)
    except Exception as Error:
        messagebox.showerror(message=Error)
        return False
        
#this works for local files 
#Do I really want to do this???
def LocalSending(Path1,Path2):
    copyfile(Path1, Path2) #src, dest

#does an ls of the remote path
def WhatsThere():
    print("here")

def trycommand():
    try:
        ToolBox.channel.exec_command('ls')
    except:
        initSSH()

def main():
    window = Tk()
    window.title("Send and Receive Files!")
    backgoundColor='#3E4149'
    buttonColor='#3E4149'#'NAVAJOWHITE'
    window.configure(background=backgoundColor)
    
    AudioOnly = BooleanVar()
    AudioOnly.set(False)
    
    MP3 = BooleanVar()
    MP3.set(False)

    enrLabel = Label(window, text="Path 1:",  bg=backgoundColor)
    enrLabel.grid(row=0, column=0, sticky=W)#, padx=(0,15))

    Path1 = Entry(window,text= "C:\\",width=25)
    Path1.grid(row=0,column=1,columnspan=3, sticky=W)
    Path1.insert(END, 'C:\\')

    enrLabel = Label(window, text="Path 2:",  bg=backgoundColor)
    enrLabel.grid(row=1, column=0, sticky=W)#, padx=(0,15))

    Path2 = Entry(window,width=25)
    Path2.grid(row=1,column=1,columnspan=3, sticky=W)
    Path2.insert(END, '/root/usr/')
    '''
    audioCheck = Checkbutton(window, text='Audio Only?', var=AudioOnly, anchor=W, bg=backgoundColor, fg='red')
    audioCheck.grid(row=2,column=0)#, sticky=W)
    '''
    #command= lambda: DNLD_YT_Audio(ytURL, AudioOnly.get(), MP3.get(), DnldDest, PrevIMG, VidInfo)
    OneToTwo = Button(window, text="Path 1 -> Path 2",fg="black" , command= lambda: SendIt(Path1.get(),Path2.get()),highlightbackground=buttonColor)
    OneToTwo.grid(row=2,column=0, columnspan=2, sticky=W)
    OneToTwo = Button(window, text="Path 2 -> Path 1",fg="black" , command= lambda: GetIt(Path1.get(),Path2.get()), highlightbackground=buttonColor)
    OneToTwo.grid(row=2,column=2, columnspan=2, sticky=W)

    ipLabel = Label(window, text="IP:",  bg=backgoundColor)
    ipLabel.grid(row=3, column=0, sticky=W)#, padx=(0,15))
    ipEntry = Entry(window, width=25)
    ipEntry.grid(row=3,column=1, sticky=W,columnspan=3)#, sticky=W)
    ipEntry.insert(END, "PixelStick.local")

    userLabel = Label(window, text="User:",  bg=backgoundColor)
    userLabel.grid(row=4, column=0, sticky=W)#, padx=(0,15))
    userEntry = Entry(window,width=10)
    userEntry.grid(row=4,column=1, sticky=W)#,columnspan=3)#, sticky=W)
    userEntry.insert(END, "pi")

    pwdLabel = Label(window, text="Pass:",  bg=backgoundColor)
    pwdLabel.grid(row=4, column=2, sticky=W)#, padx=(0,15))
    pwdEntry = Entry(window,width=10)
    pwdEntry.grid(row=4,column=3, sticky=W)#,columnspan=3)#, sticky=W)
    pwdEntry.insert(END, "0000")


    window.mainloop()


if __name__ == "__main__":
    main()