import os, paramiko, sys
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from os import walk
#from os.path import isfile, join

#this program is basically a poor man's google drive that constantly update files on the remote server whenever a local change is made
#A use case for this would be to write python on PC, but execute it on a raspberry pi


'''
To Do: 
Select local folder
Select remote Folder
See data in local folder
See data in remote folder
Compare data in each folder
Add ability to toggle whether to replace local file if remote one is newer
    By default should the local folder always have the newest file version?
        Or should whatevr is newest always take priority over both?
Replace file in remote folder with local file
Replace file in local folder with remote file
Make it check the folders on a set timer
    Add ability to adjust the timer during run time

Add ability to check and copy whole folders and everything in directories, not just the top-most files
Make logo for project. Probably in the same style as my normal PA

Make a verion that autoruns/auto selects folders without the user having to do anything

Can Python run in the Taskkbar?
    quick goolgle says maybe: https://stackoverflow.com/questions/9494739/how-to-build-a-systemtray-app-for-windows
    *.pyw - execute your script in background mode without command prompt


Extra Credit:
Add ability to select both local folders
See if there is a way to make it check only when there is a change
    How intesive is it to do a check? 
        Can it just constanly be checking times on both platforms? Or is it too intesive and should only happen on a timer


    extra extra credit: 
        add ability to select two remote folders?
        Add ability to slect different chekcing timers for each directory
            i.e. 30 seconds for local and 60 seconds for remote




'''






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
    workingDir = getDir()

    localStats = getLocalStats(workingDir)

    #channel = GetSSH()

    #channel=quickConnect()
    #sshSession(channel)



if __name__ == "__main__":
    main()