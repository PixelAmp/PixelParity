import os, paramiko, sys
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from os import walk
#from os.path import isfile, join

#this program is basically a poor man's google drive that constantly update files on the remote server whenever a local change is made
#A use case for this would be to write python on PC, but execute it on a raspberry pi



def getDir():
    messagebox.showinfo('Select Directory', 'Please the folder that will be backed up')
    WorkingDir = askdirectory()
    return WorkingDir

def getLocalStats(WorkingDir):

    localStats={}

    onlyfiles = [f for f in os.listdir(WorkingDir) if os.path.isfile(os.path.join(WorkingDir, f))]

    '''
    f = []
    for (dirpath, dirnames, filenames) in walk(WorkingDir):
        f.extend(filenames)
        break #if you don't break it will keep doing down into directories
    
    #print(repr(dirpath))
    print(dirpath)
    print('!!!!!!!!')
    print(dirnames)
    print('!!!!!!!!')
    print(filenames)
    '''


    for i in range(len(onlyfiles)):
        localStats[onlyfiles[i]]=int(os.path.getmtime(WorkingDir+'/'+onlyfiles[i]))
    
    return localStats
    
def getRemoteStats(channel):
    command = "stat -c '%Y' <filename>"

def SSHExe(channel,command):
    stdin, stdout, stderr = channel.exec_command(command,timeout=1)
    
    
    #stdin will probably never be used, unless I am bund and leave an input() command in one of the programs I write
    print("stdin")
    print(repr(stdin))
    print("!!!!!!!!!")
    print(stdin)
    print("!!!!!!!!!")
    #print('\n'.join(stdin.readlines()))

    '''
    if stdin != '':
        print("here")
        stdinResp='\n'.join(stdin.readlines())
    '''
    '''
    errorMessage='\n'.join(stderr.readlines())
    if errorMessage:
        print(repr(errorMessage))
        return errorMessage
    '''
    stdoutResp='\n'.join(stdout.readlines())
    
    print(repr(stdoutResp))
    print(stdoutResp)
    

    #return(repr(errorMessage+stdoutResp+stdinResp))




def sshSession(channel):
    command="butt"
    while command!='exit':
        command=input()
        print(SSHExe(channel,command))


def quickConnect():#ip,usr,password):
    ip='192.168.0.29'
    user='pi'
    password='0000'
    channel = paramiko.SSHClient()
    channel.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    channel.connect(ip, username=user, password=password, port=22, timeout=2)
    return channel

def GetSSH():
    Connection=False
    ip='192.168.0.29'
    user='pi'
    password='0000'

    while not Connection:

        hold=input("What is the ip of the device?\n(Leave empty for %s)\n"%ip)
        if hold != '':
            ip = hold

        hold=input("What is the username?\n(Leave empty for %s)\n"%user)
        if hold != '':
            user = hold

        hold = input("What is the password?\n(Leave empty for %s)\n"%password)
        if hold != '':
            password = hold

        try:
            channel = paramiko.SSHClient()
            channel.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            channel.connect(ip, username=user, password=password, port=22, timeout=2)
            print("Successful SSH")
            return channel
        except Exception as e:
            print("Cannot Connect")
            print(e)
            hold = input("Would you like to try to recconect? (Y/n)")
            if hold.lower() != 'y':
                sys.exit()

def main():
    #workingDir = getDir()

    #localStats = getLocalStats(workingDir)

    #channel = GetSSH()
    channel=quickConnect()
    sshSession(channel)



if __name__ == "__main__":
    main()